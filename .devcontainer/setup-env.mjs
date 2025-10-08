// Creates server/.env using Codespaces or repo environment variables
import fs from 'fs';
import path from 'path';

const root = process.cwd();
const envDir = path.join(root, 'server');
const envFile = path.join(envDir, '.env');

if (!fs.existsSync(envDir)) fs.mkdirSync(envDir, { recursive: true });

const {
  GROQ_API_KEY = '',
  GROQ_BASE_URL = 'https://api.groq.com/openai/v1',
  GROQ_MODEL = '',
  MOCK_FALLBACK = 'true',
  PORT = '8787',
  SERIES_PROVIDER = 'yahoo',
  ALPHAVANTAGE_API_KEY = '',
  POLYGON_API_KEY = ''
} = process.env;

const contents = `GROQ_API_KEY=${GROQ_API_KEY}
GROQ_BASE_URL=${GROQ_BASE_URL}
GROQ_MODEL=${GROQ_MODEL}
MOCK_FALLBACK=${MOCK_FALLBACK}
PORT=${PORT}
SERIES_PROVIDER=${SERIES_PROVIDER}
ALPHAVANTAGE_API_KEY=${ALPHAVANTAGE_API_KEY}
POLYGON_API_KEY=${POLYGON_API_KEY}
`;

if (!fs.existsSync(envFile)) {
  fs.writeFileSync(envFile, contents, 'utf8');
  console.log(`Wrote ${envFile}`);
} else {
  console.log(`${envFile} already exists; not overwriting.`);
}
