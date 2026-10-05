# Smart-Reg-Watch
# Smart Regulatory Watch Tool - Documentation Technique
 **Git Du Projet** : https://github.com/MourchidRiham/smart-reg-watch.git
 
> **Documentation technique et règles de développement**  
> **Dernière mise à jour** : Décembre 2025

---

## 📋 Table des Matières

1. [Architecture Technique](#architecture-technique)
2. [Règles de Développement](#règles-de-développement)
3. [Structure des Modules](#structure-des-modules)
4. [Modèles de Données](#modèles-de-données)
5. [Sécurité Technique](#sécurité-technique)
6. [Configuration](#configuration)
7. [Standards de Code](#standards-de-code)
8. [Gestion des Erreurs](#gestion-des-erreurs)
9. [Logging](#logging)

---

## 🏗️ Architecture Technique

### Agents

Chaque agent est un module Python indépendant avec une fonction principale `run_*_agent(state: PipelineState) -> PipelineState`.

#### Extraction Agent
- **Fichier** : `agents/extraction_agent.py`
- **Fonction** : `run_extraction_agent(state: PipelineState) -> PipelineState`
- **Responsabilités** :
  - Scraping web (Selenium + BeautifulSoup)
  - Téléchargement de fichiers
  - Validation de sécurité (avant et après téléchargement)
  - Détection de changements (SHA256 hash)
  - Extraction ZIP avec validation
- **Retour** : `state.file_paths` rempli avec les nouveaux fichiers

#### Translation Agent
- **Fichier** : `agents/translation_agent.py`
- **Fonction** : `run_translation_agent(state: PipelineState, target_language: str) -> PipelineState`
- **Responsabilités** :
  - Extraction de texte (PDF, DOCX, XLSX, CSV, XML, JSON)
  - OCR fallback pour PDF scannés
  - Traduction via Gemini 3 Pro
- **Retour** : `state.translated_text` et `state.summary` remplis

#### Keyword Analysis Agent
- **Fichier** : `agents/keyword_agent.py`
- **Fonction** : `run_keyword_agent(state: PipelineState, predefined_keywords: List[str], user_keywords: List[str], use_semantic: bool) -> PipelineState`
- **Responsabilités** :
  - Recherche regex avec contexte
  - Recherche sémantique (Sentence-Transformers)
  - Stockage des correspondances dans la base de données
- **Retour** : `state.keyword_hits` rempli (Dict[str, List[str]])

#### Notification Agent
- **Fichier** : `agents/notification_agent.py`
- **Fonction** : `run_notification_agent(state: PipelineState, recipients: List[str], send_only_if_keywords: bool) -> PipelineState`
- **Responsabilités** :
  - Construction d'email HTML
  - Envoi SMTP (SendGrid, Gmail, Outlook)
  - Gestion des erreurs d'envoi
- **Retour** : `state.errors` mis à jour si échec

#### Scheduler Agent
- **Fichier** : `agents/scheduler_agent.py`
- **Fonctions** :
  - `start_scheduler()` : Démarre le thread en arrière-plan
  - `schedule_daily_job(job_func: Callable, time_str: str)` : Planifie une tâche quotidienne
  - `stop_scheduler()` : Arrête le planificateur
- **Thread** : Daemon thread, s'arrête avec l'application

### Pipeline State

**Fichier** : `core/state.py`

```python
@dataclass
class PipelineState:
    regulator: str = "BCL"
    docs_metadata: List[dict] = field(default_factory=list)
    current_doc: Optional[dict] = None
    pdf_path: Optional[str] = None
    raw_text: str = ""
    translated_text: str = ""
    keyword_hits: Dict[str, List[str]] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    file_paths: List[str] = field(default_factory=list)
    summary: str = ""
```

**Règle** : Tous les agents reçoivent et retournent un `PipelineState`. Aucune mutation directe de variables globales.

---

## 📐 Règles de Développement

### 1. Imports

- **Ordre** : Standard library → Third-party → Local
- **Exemple** :
```python
import os
from datetime import datetime
from typing import List, Dict

from sqlmodel import SQLModel, Field
import streamlit as st

from core.state import PipelineState
from core.logging_utils import logger
```

### 2. Modèles de Base de Données

- **Localisation unique** : `utils/storage.py`
- **Règle** : Tous les modèles SQLModel doivent avoir `__table_args__ = {"extend_existing": True}`
- **Exemple** :
```python
class Document(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    # ... champs
```

### 3. Validation de Sécurité

- **Localisation** : `core/file_security_validator.py`
- **Règle** : Tous les fichiers téléchargés DOIVENT être validés avant traitement
- **Fonctions requises** :
  - `validate_file_security(filename: str, content: bytes) -> Tuple[bool, str]`
  - `validate_zip_file(zip_content: bytes) -> Tuple[bool, str]`
  - `validate_extracted_file(filepath: str) -> Tuple[bool, str]`

### 4. Gestion des Secrets

- **Règle** : JAMAIS de secrets hardcodés dans le code
- **Source** : Variables d'environnement via `.env`
- **Chargement** : `core/config.py` avec `python-dotenv`
- **Validation** : Avertissement si secret manquant

### 5. Logging

- **Règle** : JAMAIS de contenu sensible dans les logs
- **Format** : `logger.info(f"Loaded {len(items)} items (no content logged)")`
- **Hash** : Tronquer à 16 caractères : `hash[:16]`
- **Erreurs** : Type seulement, pas de stack trace complète dans logs utilisateur

### 6. Gestion des Erreurs

- **Règle** : Tous les try/except doivent logger l'erreur
- **Format** : `logger.error(f"Operation failed: {type(e).__name__}")`
- **State** : Ajouter à `state.errors` pour propagation
- **UI** : Messages génériques pour l'utilisateur

---

## 📁 Structure des Modules

### Core (`core/`)

- `config.py` : Configuration et variables d'environnement
- `state.py` : `PipelineState` dataclass
- `logging_utils.py` : Configuration du logging
- `file_security_validator.py` : Validation de sécurité des fichiers

### Agents (`agents/`)

- `extraction_agent.py` : Extraction de documents
- `translation_agent.py` : Traduction avec Gemini
- `keyword_agent.py` : Analyse de mots-clés
- `notification_agent.py` : Notifications email
- `scheduler_agent.py` : Planification

### Utils (`utils/`)

- `storage.py` : Modèles SQLModel et utilitaires DB
- `document_retriever.py` : Récupération de documents depuis DB
- `keywords_loader.py` : Chargement depuis Excel
- `agent_status.py` : Statut des agents depuis logs

### UI (`ui/`)

- `app.py` : Application Streamlit principale
- `sg_styles.py` : Styles CSS Société Générale

---

## 🗄️ Modèles de Données

### Document

```python
class Document(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: str = Field(primary_key=True)
    authority_id: str
    title: str
    url: str
    published_at: datetime | None = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    content_path: str
    translated_path: str | None = None
    hash: str
    changed: bool = False
```

**Règle** : `id` est un UUID5 basé sur l'URL : `uuid.uuid5(uuid.NAMESPACE_URL, url)`

### Match

```python
class Match(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: str = Field(primary_key=True)
    document_id: str = Field(foreign_key="document.id")
    keywords: str
    context: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Règle** : `id` format : `f"{document_id}:{keyword}:{index}"`

### RunLog

```python
class RunLog(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    authority_id: str
    status: str  # "ok", "error", "running"
    summary: str | None = None
```

---

## 🔒 Sécurité Technique

### Validation de Fichiers

#### Extensions Autorisées (Whitelist)
```python
ALLOWED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt',
    '.csv', '.xls', '.xlsx', '.ods',
    '.xml', '.json',
    '.zip', '.tar', '.gz',
}
```

#### Extensions Interdites (Denylist)
```python
DANGEROUS_EXTENSIONS = {
    '.exe', '.com', '.scr', '.bat', '.cmd', '.msi', '.ps1', '.vbs',
    '.bin', '.elf', '.dmg', '.iso',
    '.sh', '.bash', '.py', '.php', '.js',
    '.key', '.pem', '.p12', '.gpg',
    '.env', '.config', '.db', '.sqlite',
}
```

#### Limites de Taille
```python
FILE_SIZE_LIMITS = {
    '.pdf': 100 * 1024 * 1024,      # 100 MB
    '.docx': 50 * 1024 * 1024,      # 50 MB
    '.xlsx': 100 * 1024 * 1024,     # 100 MB
    '.csv': 500 * 1024 * 1024,      # 500 MB
    '.zip': 1024 * 1024 * 1024,     # 1 GB
    'default': 100 * 1024 * 1024,   # 100 MB
}
```

#### Magic Bytes
```python
MAGIC_BYTES_WHITELIST = {
    '.pdf': b'%PDF',
    '.docx': b'PK\x03\x04',
    '.xlsx': b'PK\x03\x04',
    '.zip': b'PK\x03\x04',
    '.gz': b'\x1f\x8b',
}
```

#### Signatures Dangereuses
```python
DANGEROUS_MAGIC_BYTES = {
    b'MZ',          # DOS/Windows executable
    b'#!',          # Shebang
    b'\x7fELF',     # ELF binary
    b'\xca\xfe\xba\xbe',  # Java class
}
```

### Validation ZIP

- **Limite totale** : 10 GB décompressé
- **Limite par fichier** : 500 MB
- **Limite nombre de fichiers** : 1000
- **Protection** : Path traversal, extensions dangereuses

### Hash SHA256

- **Usage** : Détection de changements
- **Stockage** : `data/versions.json` et `Document.hash`
- **Format log** : Tronqué à 16 caractères

---

## ⚙️ Configuration

### Variables d'Environnement Requises

```env
# Gemini API
GEMINI_API_KEY=...

# Tesseract & Poppler (Windows)
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
POPPLER_PATH=C:\poppler\Library\bin

# Email SMTP
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
EMAIL_USER=apikey
EMAIL_PASS=...
EMAIL_FROM=...

# UI Auth (optionnel)
APP_AUTH_TOKEN=...
```

### Configuration YAML

**Fichier** : `configs/default.yaml`

```yaml
authorities:
  - id: bcl
    name: "Banque Centrale du Luxembourg"
    feed_url: "..."
    page_url: "..."
    parser: bcl_reporting

translation:
  enabled: true
  target_languages: ["en"]
  mode: "summary"  # "full" or "summary"

keywords:
  predefined: ["AML", "CRR", "Basel"]

scheduler:
  cron: "0 8 * * *"

email:
  enabled: true
  recipients: ["team@example.com"]
```

---

## 📝 Standards de Code

### Nommage

- **Fichiers** : `snake_case.py`
- **Classes** : `PascalCase`
- **Fonctions** : `snake_case`
- **Constantes** : `UPPER_SNAKE_CASE`

### Docstrings

```python
def run_extraction_agent(state: PipelineState) -> PipelineState:
    """
    Extract documents from regulatory authority websites.
    
    Args:
        state: Pipeline state with regulator information
        
    Returns:
        Updated pipeline state with file_paths populated
        
    Raises:
        ValueError: If authority configuration is invalid
    """
```

### Type Hints

**Règle** : Toutes les fonctions publiques doivent avoir des type hints.

```python
def process_file(
    file_path: str,
    keywords: List[str],
    threshold: float = 0.5
) -> Dict[str, List[str]]:
    ...
```

---

## ⚠️ Gestion des Erreurs

### Pattern Standard

```python
try:
    result = operation()
    logger.info(f"Operation successful: {result}")
except SpecificError as e:
    logger.error(f"Operation failed: {type(e).__name__}")
    state.errors.append(f"Operation error: {str(e)}")
    return state
except Exception as e:
    logger.error(f"Unexpected error: {type(e).__name__}", exc_info=True)
    state.errors.append("Unexpected error occurred")
    return state
```

### Propagation

- **Règle** : Les erreurs sont ajoutées à `state.errors`
- **UI** : Afficher `state.errors` à l'utilisateur
- **Logs** : Logger avec `exc_info=True` pour debugging

---

## 📊 Logging

### Configuration

**Fichier** : `core/logging_utils.py`

```python
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
```

### Format

```python
# ✅ BON
logger.info(f"Loaded {len(keywords)} keywords (no content logged)")
logger.info(f"Hash verified: {hash[:16]}...")
logger.error(f"Validation failed: {error_type}")

# ❌ MAUVAIS
logger.info(f"Keywords: {keywords}")  # Contenu sensible
logger.info(f"Full hash: {hash}")     # Hash complet
logger.error(f"Error: {full_stack_trace}")  # Stack trace complète
```

### Niveaux

- **INFO** : Opérations normales, métadonnées
- **WARNING** : Situations anormales mais récupérables
- **ERROR** : Erreurs nécessitant attention
- **DEBUG** : Détails pour debugging (désactivé en production)

---

## 🔄 Flux de Données

```
1. Extraction Agent
   Input:  state.regulator
   Output: state.file_paths

2. Translation Agent
   Input:  state.file_paths
   Output: state.translated_text, state.summary

3. Keyword Analysis Agent
   Input:  state.translated_text, keywords
   Output: state.keyword_hits (saved to DB)

4. Notification Agent
   Input:  state.keyword_hits, state.summary
   Output: Email sent (or state.errors)
```

---

## 🧪 Tests Techniques

### Validation de Sécurité

```python
# Test fichier dangereux
is_valid, msg = validate_file_security("malware.exe", content)
assert not is_valid

# Test ZIP bomb
is_valid, msg = validate_zip_file(zip_bomb_content)
assert not is_valid
```

### Base de Données

```python
# Test modèle
doc = Document(id="test", authority_id="bcl", ...)
session.add(doc)
session.commit()
assert session.get(Document, "test") is not None
```

---

## 📌 Règles Importantes

1. **Pas de secrets dans le code** : Toujours `.env`
2. **Pas de contenu dans les logs** : Seulement métadonnées
3. **Validation avant traitement** : Tous les fichiers
4. **Type hints obligatoires** : Fonctions publiques
5. **Gestion d'erreurs** : Try/except avec logging
6. **State immuable** : Retourner nouveau state, pas mutation
7. **Modèles centralisés** : `utils/storage.py` uniquement
8. **Extend existing** : Tous les modèles SQLModel

---

**Dernière mise à jour** : Décembre 2025
