"""Busca semântica (RAG) em guias de psicologia."""

from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..core.config import settings
from ..core.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Gerenciador de vector store para RAG."""

    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=settings.embedding_model)
        self.vector_store = None
        self._initialize()

    def _initialize(self) -> None:
        """Inicializa ou carrega vector store."""
        if settings.vector_store_path.exists():
            logger.info("Carregando vector store existente")
            self.vector_store = FAISS.load_local(
                str(settings.vector_store_path),
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
        else:
            logger.info("Criando novo vector store")
            self._build_vector_store()

    def _build_vector_store(self) -> None:
        """Constrói vector store a partir dos guias."""
        guides_path = settings.psychology_guides_path

        if not guides_path.exists():
            logger.warning("Pasta de guias não encontrada, criando vector store vazio")
            guides_path.mkdir(parents=True, exist_ok=True)
            return

        # Carrega documentos
        loader = DirectoryLoader(
            str(guides_path),
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
        )

        try:
            documents = loader.load()

            if not documents:
                logger.warning("Nenhum documento encontrado para indexar")
                return

            # Split em chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            chunks = text_splitter.split_documents(documents)

            # Cria vector store
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)

            # Salva
            settings.vector_store_path.parent.mkdir(parents=True, exist_ok=True)
            self.vector_store.save_local(str(settings.vector_store_path))

            logger.info(
                "Vector store criado com sucesso",
                documents_count=len(documents),
                chunks_count=len(chunks),
            )

        except Exception as e:
            logger.error("Erro ao construir vector store", error=str(type(e).__name__))

    def search(self, query: str, k: int | None = None) -> str:
        """Busca contexto relevante."""
        if not self.vector_store:
            logger.warning("Vector store não disponível")
            return "Nenhum contexto adicional disponível."

        k = k or settings.top_k_retrieval

        try:
            docs = self.vector_store.similarity_search(query, k=k)

            if not docs:
                return "Nenhum contexto relevante encontrado."

            # Concatena resultados
            context = "\n\n".join([doc.page_content for doc in docs])

            logger.info("Contexto recuperado", docs_count=len(docs))
            return context

        except Exception as e:
            logger.error("Erro ao buscar contexto", error=str(type(e).__name__))
            return "Erro ao recuperar contexto."

    def rebuild(self) -> None:
        """Reconstrói vector store do zero."""
        logger.info("Reconstruindo vector store")
        if settings.vector_store_path.exists():
            import shutil

            shutil.rmtree(settings.vector_store_path)
        self._build_vector_store()


# Singleton
vector_store = VectorStore()
