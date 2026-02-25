$env:DATABASE_URL = "postgresql://ham_agent_2:ham_agent_2_password@localhost:5432/ham_agent_2_db"
Set-Location packages\backend
npm run dev
