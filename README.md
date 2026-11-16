# Soc Simulator Project

Utilisation de `uv` pour avoir un gain de temps considérable dans l'exécution des commandes.

## Setup

### Créer l'environnement virtuel

Se mettre dans le dossier de l'un des micro-services pour faire la commande suivante :

```shell
    uv venv
```

Il devrait afficher en sortie :

```console
Using CPython 3.13.5
Creating virtual environment at: .venv
Activate with: .venv\Scripts\activate
```

### Activer l'environnement virtuel

Avec un environnement ``Windows (PowerShell)`` :

```shell
    .\.venv\Scripts\Activate
```

Avec un environnement ``Mac/Linux`` :

```shell
    source .venv/bin/activate
```

### Installer les dépendances

Chaque dossier comprend un micro-service différent avec des dépendances propres à chacun. Pour installer ces dépendances, il suffit d'être dans le dossier et d'exécuter le ``requirements.txt``.

```shell
    cd alert-engine
    uv pip install -r requirements.txt
```
