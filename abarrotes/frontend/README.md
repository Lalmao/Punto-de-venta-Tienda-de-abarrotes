# Frontend React — Abarrotes Placencia

Va DENTRO de la carpeta `abarrotes`, junto a `app/`:

    abarrotes/
    ├─ app/          (backend Python)
    ├─ frontend/     (esto)
    └─ ...

## Instalación (una vez)
1. Instala Node.js (versión LTS): https://nodejs.org
2. En una terminal:

       cd frontend
       npm install

## Uso diario (2 terminales abiertas a la vez)
Terminal 1 (backend), en la carpeta `abarrotes`:

    venv\Scripts\activate
    uvicorn app.main:app --reload

Terminal 2 (frontend), en la carpeta `abarrotes/frontend`:

    npm run dev

Abre **http://localhost:5173**
