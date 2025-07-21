

# Now
- Build complete workflow following https://python.langchain.com/docs/tutorials/rag/#setup

- Add better pdf chunking either max number of tokens or recursive, or other.

# Parse pdfs better

- Exploit some of the structure in the pdf (sections, tables, etc.), follow very good instructions here: https://python.langchain.com/docs/how_to/document_loader_pdf/#simple-and-fast-text-extraction
- Better parsing for academic papers! https://python.langchain.com/docs/integrations/document_loaders/grobid/
- Follow this documentation as well: https://python.langchain.com/docs/tutorials/retrievers/

## Unstructured PDF parsing
Check out: https://python.langchain.com/docs/how_to/document_loader_pdf/#local-parsing

# RAG app tutorial:
- This single page has all I need: https://python.langchain.com/docs/tutorials/rag/#setup


# Anonimize info
- https://github.com/deepanwadhwa/zink?tab=readme-ov-file

# Improve UI
- Build a chat interface in streamlit: https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps


# Install, need to add to docker image later
## PDF parsing
sudo apt install poppler-utils
sudo apt install tesseract-ocr



# App structure
1. Index pdf documents:
    - load, split -> unstructured pdf maybe too much: not needed?
    - embeddings -> Ollama + chroma

# Docker workflow
In order to remove previous versions of docker images that are taking up space:
`docker image prune --filter label=project=talensinki`

# Preguntas Clara
- Vas a necesitar buscar en un subconjunto de los archivos? Ejemplo: buscar en todos los archivos creados después de 2010.
- Firmar acuerdo de que la propiedad intelectual del cacharro (quitando las cosas sensitivas) me pertenece. Hacer una license que no permita el uso comercial!

