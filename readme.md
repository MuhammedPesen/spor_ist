Automate booking sessions on Spor Istanbul. This script logs in, selects available sessions, handles CAPTCHA challenges using OpenAI, and finalizes your booking automatically. I created this because sessions often become full too quickly. With this tool, it continuously checks for available sessions every 30 seconds and automatically takes a session if it becomes available due to someone deselecting it.

Note: Some parts of the script are hardcoded and may require tweaking to fit your specific needs.


### Prerequisites
- **Python 3.8+**
- **Playwright**: Install browsers with `playwright install`.
- **OpenAI API Key**: For CAPTCHA solving.
- **Environment Variables**: Your credentials and OpenAI API key.

### Installation
#### Clone the Repository
```bash
git clone https://github.com/MuhammedPesen/spor_ist.git
cd spor_ist
```

#### Create a Virtual Environment (Optional/Choose One)
```bash
python -m venv venv
source venv/bin/activate
```

```bash
conda create --name spor_ist python=3.8
conda activate spor_ist
```


#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Install Playwright Browsers
```bash
playwright install
```

### Configuration
#### Create a .env File
In the root directory, create a `.env` file based on `.env_example`:
```bash
cp .env.example .env
```

### Usage
Run the script with optional flags for headless mode and verbose output:
```bash
python src/main.py [--headless] [--verbose]
```
- `--headless`: Run the browser without a UI.
- `--verbose`: Enable logging.

#### Examples
**Headless with Verbose Logging**
```bash
python src/main.py --headless --verbose
```