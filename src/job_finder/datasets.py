# import pickle
# import fsspec
import json
import logging
import os
import pickle
from typing import Any, Dict, List, Optional

import chromadb
import pandas as pd
from kedro.io.core import AbstractDataset, DatasetError
from kedro_datasets.pickle import PickleDataset
from kedro_datasets.json import JSONDataset
from sentence_transformers import SentenceTransformer

# from kedro.io.core import get_filepath_str, get_protocol_and_path
# from pathlib import PurePosixPath
# from typing import Any


# from kedro.io import AbstractVersionedDataset


log = logging.getLogger(__name__)


class OptionalPickleDataset(PickleDataset):
    """Custom PickleDataset that does not fail if file is missing."""

    def _load(self):
        try:
            return super()._load()
        except FileNotFoundError:
            log.warning(
                f"[OptionalPickleDataset] Fichier "
                f"{self._filepath} introuvable, retourne None."
            )
            return None
        except (EOFError, pickle.UnpicklingError):
            log.warning(
                f"[OptionalPickleDataset] Fichier "
                f"{self._filepath} vide ou corrompu, retourne None."
            )
            return None
        except DatasetError as e:
            if "Did not find any versions" in str(e):
                log.warning(
                    f"[OptionalPickleDataset] Aucune "
                    f"version trouvée pour {self._filepath}, retourne None."
                )
                return None
            raise e


class ChromaDataset(AbstractDataset):
    """Custom dataset for ChromaDB integration with job data.
    
    Supports both local and remote ChromaDB configurations via parameters.
    """

    def __init__(
        self,
        collection_name: str = "jobs",
        persist_directory: str = "./data/chroma",
        embedding_model: str = "intfloat/multilingual-e5-small",
        chroma_host: str = None,
        chroma_port: int = 8000,
        chroma_ssl: bool = False,
        **kwargs
    ):
        """Initialize ChromaDB dataset with flexible configuration.
        
        Args:
            collection_name: Name of the Chroma collection
            persist_directory: Directory to persist ChromaDB data (local mode)
            embedding_model: SentenceTransformers model for embeddings
            chroma_host: Remote ChromaDB host (if None, uses local mode)
            chroma_port: Remote ChromaDB port (default 8000)
            chroma_ssl: Use SSL for remote connection (default False)
        """
        self._collection_name = collection_name
        self._embedding_model = embedding_model
        
        # Configuration ChromaDB flexible
        log.info(f"🔧 ChromaDataset __init__ parameters:")
        log.info(f"   collection_name: {collection_name}")
        log.info(f"   persist_directory: {persist_directory}")
        log.info(f"   chroma_host: {chroma_host}")
        log.info(f"   chroma_port: {chroma_port}")
        log.info(f"   chroma_ssl: {chroma_ssl} (type: {type(chroma_ssl)})")
        log.info(f"   embedding_model: {embedding_model}")
        
        if chroma_host:
            # Mode distant - properly convert SSL string to boolean
            ssl_value = chroma_ssl
            if isinstance(chroma_ssl, str):
                ssl_value = chroma_ssl.lower() in ('true', '1', 'yes', 'on')
            else:
                ssl_value = bool(chroma_ssl)
            
            self._chroma_config = {
                "mode": "remote",
                "host": chroma_host,
                "port": int(chroma_port),
                "ssl": ssl_value
            }
            log.info(f"✅ ChromaDataset configured for REMOTE mode:")
            log.info(f"   Host: {chroma_host}")
            log.info(f"   Port: {chroma_port}")
            log.info(f"   SSL: {chroma_ssl} -> {ssl_value}")
        else:
            # Mode local
            self._chroma_config = {
                "mode": "local",
                "path": persist_directory
            }
            log.info(f"✅ ChromaDataset configured for LOCAL mode: {persist_directory}")
        
        self._client = None
        self._collection = None
        self._sentence_transformer = None

    def _get_client(self) -> chromadb.Client:
        """Get or create ChromaDB client based on configuration."""
        if self._client is None:
            config = self._chroma_config
            
            if config["mode"] == "remote":
                log.info(f"🌐 Attempting to connect to REMOTE ChromaDB:")
                log.info(f"   Host: {config['host']}")
                log.info(f"   Port: {config['port']}")
                log.info(f"   SSL: {config.get('ssl', False)}")
                log.info(f"   Full config: {config}")
                
                try:
                    ssl_setting = config.get('ssl', False)
                    log.info(f"🔐 Creating HttpClient with SSL={ssl_setting}")
                    
                    self._client = chromadb.HttpClient(
                        host=config['host'],
                        port=config['port'],
                        ssl=ssl_setting
                    )
                    log.info("✅ ChromaDB HttpClient created successfully")
                    
                    # Test the connection
                    log.info("🧪 Testing ChromaDB connection...")
                    heartbeat = self._client.heartbeat()
                    log.info(f"💓 ChromaDB heartbeat successful: {heartbeat}")
                    
                except Exception as e:
                    log.error(f"❌ Failed to connect to remote ChromaDB:")
                    log.error(f"   Error type: {type(e).__name__}")
                    log.error(f"   Error message: {str(e)}")
                    log.error(f"   Config used: {config}")
                    raise
            else:
                log.info(f"Connecting to local ChromaDB at {config['path']}")
                try:
                    # S'assurer que le dossier existe
                    os.makedirs(config['path'], exist_ok=True)
                    self._client = chromadb.PersistentClient(path=config['path'])
                    log.info("✅ Connected to local ChromaDB successfully")
                except Exception as e:
                    log.error(f"❌ Failed to connect to local ChromaDB: {e}")
                    raise
        return self._client

    def _get_collection(self) -> chromadb.Collection:
        """Get or create ChromaDB collection."""
        if self._collection is None:
            client = self._get_client()
            # Try to get existing collection, create if doesn't exist
            try:
                self._collection = client.get_collection(self._collection_name)
                log.info(f"Retrieved existing collection: {self._collection_name}")
            except Exception:
                self._collection = client.create_collection(self._collection_name)
                log.info(f"Created new collection: {self._collection_name}")
        return self._collection

    def _get_embedding_model(self) -> SentenceTransformer:
        """Get or create sentence transformer model."""
        if self._sentence_transformer is None:
            log.info(f"Loading embedding model: {self._embedding_model}")
            self._sentence_transformer = SentenceTransformer(self._embedding_model)
        return self._sentence_transformer

    def _create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts."""
        model = self._get_embedding_model()
        embeddings = model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()

    def _prepare_job_data(self, jobs_df: pd.DataFrame) -> tuple:
        """Prepare job data for ChromaDB storage.
        
        Returns:
            Tuple of (ids, embeddings, documents, metadatas)
        """
        ids = []
        documents = []
        metadatas = []

        for idx, job in jobs_df.iterrows():
            # Create unique ID for each job
            job_id = f"job_{job.get('reference', idx)}_{job.get('company_slug', 'unknown')}"
            ids.append(job_id)

            # Use preprocessed embedding text if available, otherwise fallback to old method
            if 'embedding_text' in job and job['embedding_text']:
                doc_text = job['embedding_text']
            else:
                # Fallback: Create document text for embedding (title + description)
                doc_text = f"{job.get('name', '')} {job.get('description', '')}"
            
            documents.append(doc_text)

            # Store all other fields as metadata
            metadata = {
                "company_name": job.get("company_name", ""),
                "company_slug": job.get("company_slug", ""),
                "publication_date": str(job.get("publication_date", "")),
                "city": job.get("city", ""),
                "country": job.get("country", ""),
                "remote": job.get("remote", ""),
                "education_level": job.get("education_level", ""),
                "url": job.get("url", ""),
                "reference": str(job.get("reference", "")),
                "name": job.get("name", ""),
                "slug": job.get("slug", ""),
                "salary_min": str(job.get("salary_min", "")),
                "salary_max": str(job.get("salary_max", "")),
                "salary_currency": job.get("salary_currency", ""),
            }
            # Remove empty values to keep metadata clean
            metadata = {k: v for k, v in metadata.items() if v and v != "nan"}
            metadatas.append(metadata)

        # Create embeddings for all documents
        embeddings = self._create_embeddings(documents)

        return ids, embeddings, documents, metadatas

    def _load(self) -> pd.DataFrame:
        """Load data from ChromaDB and return as DataFrame."""
        collection = self._get_collection()
        
        # Get all documents from collection
        results = collection.get(include=["metadatas", "documents", "embeddings"])
        
        if not results["ids"]:
            log.warning("No data found in ChromaDB collection")
            return pd.DataFrame()

        # Convert back to DataFrame
        data = []
        for metadata in results["metadatas"]:
            data.append(metadata)
        
        df = pd.DataFrame(data)
        log.info(f"Loaded {len(df)} jobs from ChromaDB")
        return df

    def _save(self, data: pd.DataFrame) -> None:
        """Save job data to ChromaDB."""
        if data.empty:
            log.warning("Empty DataFrame provided, nothing to save")
            return

        collection = self._get_collection()
        
        # Prepare data for ChromaDB
        ids, embeddings, documents, metadatas = self._prepare_job_data(data)
        
        log.info(f"Saving {len(ids)} jobs to ChromaDB collection: {self._collection_name}")
        
        # Upsert data (add or update)
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        log.info(f"Successfully saved {len(ids)} jobs to ChromaDB")

    def query_similar_jobs(
        self, 
        query_text: str, 
        n_results: int = 5, 
        where_filter: Optional[Dict] = None
    ) -> List[Dict]:
        """Query similar jobs based on text similarity.
        
        Args:
            query_text: Text to search for (e.g., CV content)
            n_results: Number of similar jobs to return
            where_filter: Optional metadata filter
            
        Returns:
            List of similar jobs with metadata and similarity scores
        """
        collection = self._get_collection()
        
        # Create embedding for query
        query_embedding = self._create_embeddings([query_text])[0]
        
        # Search similar jobs
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter,
            include=["metadatas", "documents", "distances"]
        )
        
        # Format results
        similar_jobs = []
        for i in range(len(results["ids"][0])):
            job = {
                "id": results["ids"][0][i],
                "metadata": results["metadatas"][0][i],
                "document": results["documents"][0][i],
                "similarity_score": 1 - results["distances"][0][i],  # Convert distance to similarity
            }
            similar_jobs.append(job)
        
        return similar_jobs

    def _describe(self) -> Dict[str, Any]:
        """Describe the dataset."""
        config_desc = {
            "collection_name": self._collection_name,
            "embedding_model": self._embedding_model,
        }
        
        # Ajouter les détails de configuration ChromaDB
        if self._chroma_config["mode"] == "remote":
            config_desc.update({
                "chroma_mode": "remote",
                "chroma_host": self._chroma_config["host"],
                "chroma_port": self._chroma_config["port"],
                "chroma_ssl": self._chroma_config.get("ssl", False)
            })
        else:
            config_desc.update({
                "chroma_mode": "local",
                "persist_directory": self._chroma_config["path"]
            })

        return config_desc


# class OptionalPickleDataset(AbstractVersionedDataset):
#     """Custom PickleDataset that does not fail if file is missing."""
#
#     def __init__(
#         self,
#         filepath: str,
#         version=None,
#         credentials: dict = None,
#         load_args: dict = None,
#         save_args: dict = None,
#     ):
#         # Kedro internally expects a Path-like object here
#         self._filepath = PurePosixPath(filepath)
#         self._protocol, self._path = get_protocol_and_path(filepath, version)
#         self._credentials = credentials or {}
#         self._fs = fsspec.filesystem(self._protocol, **self._credentials)
#
#         self._load_args = load_args or {}
#         self._save_args = save_args or {}
#
#         super().__init__(filepath=self._filepath, version=version)
#
#     def _load(self) -> Any:
#         load_path = self._get_load_path()
#         try:
#             with self._fs.open(load_path, mode="rb") as f:
#                 return pickle.load(f, **self._load_args)
#         except (FileNotFoundError, EOFError):
#             return None
#
#     def _save(self, data: Any) -> None:
#         save_path = self._get_save_path()
#         with self._fs.open(save_path, mode="wb") as f:
#             pickle.dump(data, f, **self._save_args)
#
#     def _get_load_path(self) -> str:
#         if self._version and self._version.load:
#             return f"{self._path}/{self._version.load}/{self._filepath.name}"
#         return str(self._path)
#
#     def _get_save_path(self) -> str:
#         if self._version and self._version.save:
#             return f"{self._path}/{self._version.save}/{self._filepath.name}"
#         return str(self._path)
#
#     def _get_versioned_path(self, version: str) -> PurePosixPath:
#         # Required for Kedro to compute versioned save/load directories
#         return PurePosixPath(self._filepath) / version / self._filepath.name
#
#     def _describe(self) -> dict:
#         return {
#             "filepath": str(self._filepath),
#             "version": self._version,
#             "protocol": self._protocol,
#         }


class OptionalJSONDataset(JSONDataset):
    """
    JSON dataset that returns empty dict if file doesn't exist or is invalid.
    Useful for optional files like job_likes.json that might not exist initially.
    """
    
    def __init__(self, *args, default_data: Any = None, **kwargs):
        """
        Initialize OptionalJSONDataset.
        
        Args:
            default_data: Default data to return if file doesn't exist or is invalid.
                         Defaults to empty dict.
        """
        super().__init__(*args, **kwargs)
        self._default_data = default_data if default_data is not None else {}
    
    def _load(self) -> Any:
        """
        Load JSON data, returning default_data if file doesn't exist or is invalid.
        
        Returns:
            Loaded JSON data or default_data if file is missing/invalid.
        """
        try:
            return super()._load()
        except (FileNotFoundError, json.JSONDecodeError, DatasetError) as exc:
            log.warning(
                f"Could not load {self._filepath}: {exc}. "
                f"Returning default data: {self._default_data}"
            )
            return self._default_data
    
    def _exists(self) -> bool:
        """
        Check if dataset exists, but don't fail if it doesn't.
        
        Returns:
            True if file exists and is valid, False otherwise.
        """
        try:
            return super()._exists()
        except Exception:
            return False
