# FisioAccess

Software para la toma de electrocardiograma

## Description

This project was created with PySide6 and Python.

## Author

- **Vanessa**
- Email: vanessauribe858@gmail.com
- Organization: Uach

## Version

1.0.0

## License

This project is under the MIT license.

## Project Structure

```
src/
├── config/        # Configuration files
├── ui/            # User interface components
│   ├── dialogs/   # Dialog windows
│   └── views/     # View components
├── models/        # Data models
└── utils/         # Utility functions

resources/
├── images/        # Images and icons
├── styles/        # Style sheets
├── icons/         # Application icons
└── translations/  # Language files
    ├── es.ts     # Spanish translation source
    ├── es.qm     # Compiled Spanish translation
    ├── en.ts     # English translation source
    └── en.qm     # Compiled English translation
```

## Requirements

- Python 3.12+
- PySide6
- Qt6 tools (for translations)
- Other dependencies in requirements.txt

## Installation

1. Clone the repository
2. Activate virtual environment: `source activate_env.sh`
3. Install dependencies: `pip install -r requirements.txt`
4. Compile translations: `./compile_translations.sh`

## Translations

### Adding a New Language

1. Create a new translation file (example for French):
   ```bash
   # Create fr.ts file in resources/translations/
   <?xml version="1.0" encoding="utf-8"?>
   <!DOCTYPE TS>
   <TS version="2.1" language="fr">
   <context>
       <name>MainWindow</name>
       <message>
           <source>Welcome to {}</source>
           <translation>Bienvenue à {}</translation>
       </message>
       <!-- Add more translations here -->
   </context>
   </TS>
   ```

2. Add the new language to compile_translations.sh:
   ```bash
    resources/translations/fr.ts -qm resources/translations/fr.qm
   ```

3. Compile translations:
   ```bash
   ./compile_translations.sh
   ```

### Creating Translation Files

The easiest way to create translation files is using Qt Linguist:

1. Install Qt6 Linguist:
   - Ubuntu/Debian: `sudo apt-get install qt6-tools-dev`
   - Fedora: `sudo dnf install qt6-linguist`
   - Arch: `sudo pacman -S qt6-tools`

2. Generate translation files:
   ```bash
   # Create/update .ts files
   lupdate-qt6 src/ -ts resources/translations/es.ts
   ```

3. Edit translations using Qt Linguist:
   ```bash
   linguist-qt6 resources/translations/es.ts
   ```

4. Compile translations:
   ```bash
   ./compile_translations.sh
   ```

## Building

To compile the project, run:

```bash
./compile.sh
```

## Usage

To run in development mode:

```bash
python src/main.py
```
