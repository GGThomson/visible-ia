# Fase C3 · Motor de consultas

**Objetivo:** hacer una corrida real de un mercado: 10 preguntas × 3 repeticiones en ChatGPT (API) y en Google Modo IA (SerpApi).
- Se guarda cada respuesta con sus fuentes y su costo.
- Es reanudable y respeta el tope de presupuesto.
- Además, se pueden cargar muestras manuales de las apps (Gemini y ChatGPT).

**Historias que cubre:** HU-04, HU-05, HU-06
**Estado:** ⚪ pendiente
**Depende de (Director):** cuenta de SerpApi (plan gratis) y **facturación de OpenAI aprobada y activada**, con las claves en `.env` y en Secrets.

## Tareas

### C3-T01 · Cliente de ChatGPT (Responses API + web search)
- **Estado:** ⚪
- **Qué:** `motor/chatgpt_api.py` con una función `consultar(pregunta) -> RespuestaMotor`.
  - Usa el SDK oficial `openai`: Responses API, modelo `gpt-5-mini`, herramienta `web_search` con `user_location` aproximada (`country="PE"`, `city="Lima"`, `region="Lima"`, `timezone="America/Lima"`).
  - Devuelve el texto, las citas (URL y título), el n.º de búsquedas hechas, los tokens, el costo estimado y el JSON crudo.
- **Archivos probables:** `src/visible_ia/motor/chatgpt_api.py`, `src/visible_ia/motor/modelos.py` (pydantic), `tests/unit/test_chatgpt_api.py`, `tests/fixtures/openai_response.json`
- **Criterios de aceptación:**
  - [ ] Con una respuesta grabada (fixture), el parseo extrae el texto, las citas y los tokens.
  - [ ] Costo estimado = búsquedas × US$0.01 + tokens × tarifa. Las tarifas van en una tabla de configuración con su fecha, no fijas en el código.
  - [ ] Los errores 429 y 5xx se reintentan hasta 3 veces con espera creciente. El resto se propaga.
- **Pruebas:** unitarias con la fixture. Una prueba `@pytest.mark.live` (se salta por defecto) hace 1 llamada real.
- **Depende de:** C1-T02
- **Rama:** `feat/C3-T01-chatgpt-client`
- **Notas para Claude Code:**
  - Verificar en la documentación de OpenAI, al implementarlo, el nombre exacto de la herramienta y de los campos de ubicación. Si difieren de estas notas, gana la documentación y se anota en el PR.
  - No usar la app de ChatGPT ni navegar su web (ADR-002).

### C3-T02 · Cliente de Google Modo IA (SerpApi)
- **Estado:** ⚪
- **Qué:** `motor/google_ai_mode.py`, con la misma interfaz que C3-T01.
  - Parámetros: `engine=google_ai_mode`, `q`, `location="Lima, Peru"`, `hl=es`, `gl=pe`.
  - El texto sale de los bloques de texto (o del markdown reconstruido); las fuentes, de `references`.
- **Archivos probables:** `src/visible_ia/motor/google_ai_mode.py`, `tests/unit/test_google_ai_mode.py`, `tests/fixtures/serpapi_ai_mode.json`
- **Criterios de aceptación:**
  - [ ] Parsea la fixture (texto y referencias).
  - [ ] **Verificación (tarea legal de la estrategia):** una llamada real confirma que una búsqueda consume 1 crédito (se mira en la cuenta de SerpApi) y que acepta Lima y español. El resultado se anota en `riesgo-legal-motor.md` §4.
  - [ ] Si SerpApi devuelve "sin respuesta de IA", se guarda como respuesta vacía marcada, no como error.
- **Pruebas:** unitarias con la fixture, más una prueba `live` opcional.
- **Depende de:** C1-T02
- **Rama:** `feat/C3-T02-serpapi-client`
- **Notas para Claude Code:** usar `httpx` directamente (sin el SDK de SerpApi) para tener control de los reintentos.

### C3-T03 · Presupuesto y cuota (HU-05)
- **Estado:** ⚪
- **Qué:** `motor/presupuesto.py`.
  - Antes de una corrida calcula su costo estimado (OpenAI) y cuántas búsquedas consume (SerpApi).
  - Suma lo gastado en el mes calendario (zona America/Lima).
  - **Bloquea** si se superaría `MONTHLY_BUDGET_USD` o la cuota de SerpApi (configurable, por defecto 250), y explica cuánto costaría.
- **Archivos probables:** `src/visible_ia/motor/presupuesto.py`, `tests/unit/test_presupuesto.py`
- **Criterios de aceptación:**
  - [ ] Los criterios de presupuesto de HU-04/HU-05 del PRD §4.
  - [ ] Opción `--forzar` solo con la confirmación explícita en la terminal ("escribe SI"). Queda registrado en la corrida.
- **Pruebas:** escenarios dentro del tope, justo en el tope y por encima; cambio de mes.
- **Depende de:** C3-T01, C3-T02
- **Rama:** `feat/C3-T03-budget-guard`

### C3-T04 · Corrida reanudable (HU-04)
- **Estado:** ⚪
- **Qué:** `motor/corrida.py` y el comando `visible-ia corrida lanzar --mercado <id> [--superficies chatgpt_api,google_ai_mode] [--reps 3]`.
  - Crea la corrida, ejecuta las llamadas que faltan y guarda cada `respuesta` y sus `fuente` apenas llegan.
  - Marca la corrida como `completa` o `incompleta`.
  - `visible-ia corrida reanudar <id>` hace solo lo que falta.
  - `visible-ia corrida ver <id>` muestra el avance y el costo.
- **Archivos probables:** `src/visible_ia/motor/corrida.py`, `src/visible_ia/cli.py`, `tests/unit/test_corrida.py`, `tests/integration/test_corrida_db.py`
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-04 del PRD §4 (guarda cada campo; es reanudable sin repetir).
  - [ ] Una corrida de 60 llamadas termina en ≤ 20 min (PRD §6).
  - [ ] Si se corta a mitad (Ctrl+C), `reanudar` completa sin duplicados.
- **Pruebas:** clientes falsos que fallan en la llamada n.º 7; verificar la reanudación y la unicidad (corrida, pregunta, superficie, repetición).
- **Depende de:** C3-T03, C2-T02
- **Rama:** `feat/C3-T04-resumable-run`
- **Notas para Claude Code:**
  - Hasta 3 llamadas concurrentes por superficie, como máximo.
  - Los dominios de las fuentes se guardan normalizados (sin `www.` y sin parámetros `utm_*`).

### C3-T05 · Carga de muestras manuales (HU-06)
- **Estado:** ⚪
- **Qué:** comando `visible-ia muestra cargar --mercado <id> --pregunta <n> --superficie gemini_app_manual|chatgpt_app_manual`.
  - Abre el editor, o lee de un archivo, para pegar la respuesta y las fuentes.
  - La guarda en una corrida de tipo `manual`.
  - Otra opción: importar desde un CSV con el formato de `registro.csv` de la fase 1.
- **Archivos probables:** `src/visible_ia/motor/manual.py`, `tests/unit/test_manual.py`
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-06 del PRD §4: marcada como "manual / app"; **no entra al índice**.
  - [ ] Importa `docs/01-descubrimiento/prueba-fuentes/registro.csv` sin errores. Esto sirve para el conjunto de evaluación de C4.
- **Pruebas:** importar ese CSV real y contar las filas por superficie.
- **Depende de:** C3-T04
- **Rama:** `feat/C3-T05-manual-samples`

## Demo de la fase
- El Director lanza la corrida real de "Implantología · Miraflores".
- Ve el avance y el costo (≈ US$0.75).
- La corta a mitad y la reanuda.
- Carga una respuesta de la app de Gemini pegándola.
