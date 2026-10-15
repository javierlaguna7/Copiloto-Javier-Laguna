# Copiloto Clínico APS

Aplicación de apoyo a la decisión clínica para medicina general y atención primaria en Colombia. A partir del caso clínico (enfermedad actual, revisión por sistemas, antecedentes, alergias, signos vitales, examen físico, laboratorios e informes de imágenes) propone diagnósticos diferenciales ordenados por probabilidad relativa, diagnóstico sindromático, entidades que no se deben pasar por alto, estudios con hallazgos esperados, tratamiento por fases, seguimiento, criterios de remisión y signos de alarma.

> **Uso exclusivo de profesionales de la salud.** Es una herramienta de apoyo: no reemplaza el juicio clínico ni ha sido validada con pacientes reales. Ver [Seguridad y limitaciones](#seguridad-y-limitaciones).

## Contenido

- 725 patologías y condiciones con generalidades (principios, epidemiología, etiología, fisiopatología), síntomas y signos, examen dirigido, criterios y escalas, algoritmos, estudios con hallazgos esperados, farmacoterapia por fases, metas, seguimiento, remisión y alarmas.
- 60 síndromes clínicos, 144 reglas de «no pasar por alto» y 89 escalas y calculadoras.
- Lectura de laboratorios (118 analitos con rangos por edad, sexo y gestación) e informes de imágenes, ECG y patología; carga de PDF y fotos (OCR).
- Glosario emergente de siglas, signos y maniobras (unas 2.500 entradas) al tocar o pasar el cursor.
- Capa de seguridad: plausibilidad de signos vitales, umbral de SpO₂ por altitud, estado de embarazo y puerperio, alergias medicamentosas con reactividad cruzada, TFG (CKD-EPI 2021) y contraindicaciones.
- Historia de pacientes local, temas y tamaño de letra, dictado por voz.
- Funciona sin conexión después de la primera carga (PWA). El dictado por voz, la lectura de PDF y el OCR necesitan internet.

## Estructura

```
src/            Código fuente
  shell.html      Estilos y estructura de la página
  app.js          Interfaz (sin reglas clínicas)
  engine.js       Motor diagnóstico
  safety.js       Capa de seguridad clínica
  personalize.js  Ajuste por edad, sexo, embarazo, función renal y alergias
  lexicon*.js, lexsyn*.js   Léxico semiológico y sinónimos latinoamericanos
  db1..db29.js    Base de conocimiento (725 entidades)
  addenda*.js, extra*.js, info*.js   Secciones complementarias por entidad
  labs.js, labref.js, calc.js, cantmiss.js, syndromes.js, glossary.js, gloss*.js, glos*.js, qa*.js
assets/         Ícono maestro (SVG) e íconos PNG generados
spec/           Pruebas y validadores
  safety/       Pruebas de seguridad clínica
  qa/           Viñetas clínicas de regresión (test1–4) y conjunto independiente (holdout)
  modulos/      Pruebas de calculadoras, laboratorios y «no pasar por alto»
  check.js      Validador de formato de la base de conocimiento
docs/           Aplicación compilada lista para publicar (GitHub Pages)
build.py        Compila src/ → docs/ y corre todas las pruebas
```

## Compilar y probar

Requisitos: Python 3.10+ y Node.js 18+.

```bash
python3 build.py          # corre las pruebas; si alguna falla, no compila
npm test                  # solo las pruebas
npm run serve             # sirve docs/ en http://localhost:8080
```

`build.py` genera `docs/` (la PWA: index.html, manifest, service worker e íconos). Si Playwright está instalado (`pip install playwright && playwright install chromium`), regenera los íconos desde `assets/icon.svg`; si no, usa los PNG de `assets/icons/`.

Para validar una entidad nueva o editada: `node spec/check.js src/dbNN.js`.

## Publicar en GitHub

1. Cree un repositorio nuevo en GitHub (puede ser privado, aunque GitHub Pages en repositorios privados requiere un plan de pago).
2. Suba el contenido de esta carpeta:
   ```bash
   git init
   git add .
   git commit -m "Copiloto Clínico APS v6"
   git branch -M main
   git remote add origin https://github.com/USUARIO/copiloto-clinico.git
   git push -u origin main
   ```
3. En el repositorio: **Settings → Pages → Build and deployment → Source: Deploy from a branch**, rama `main`, carpeta `/docs`. En uno o dos minutos la app queda en `https://USUARIO.github.io/copiloto-clinico/`.
4. Cada cambio en `src/`: ejecute `python3 build.py` y suba también `docs/`. El flujo de GitHub Actions (`.github/workflows/ci.yml`) compila y corre todas las pruebas en cada envío.

## Generar el APK para Android

1. Con la app publicada en GitHub Pages, abra https://www.pwabuilder.com e ingrese la dirección.
2. Elija **Android → Generate package**. Descargue el paquete (incluye el APK/AAB y la clave de firma; guárdela, la necesitará para actualizar).
3. Instale el APK en el teléfono, o suba el AAB a Google Play.

Para que el APK abra sin barra del navegador, PWABuilder indica cómo publicar el archivo `assetlinks.json` en `docs/.well-known/`.

## Seguridad y limitaciones

- Las viñetas de prueba se escribieron en el mismo proceso que ajustó el motor; en un conjunto independiente, antes de ajustarlo, la precisión fue del 94 % en los tres primeros diagnósticos. Antes de cualquier uso clínico real se requiere validación con historias reales anonimizadas y revisión por especialistas.
- No revisa interacciones entre medicamentos ni recibe la lista de medicamentos actuales de forma estructurada.
- La lectura de texto libre se basa en un léxico: frases ambiguas o con errores pueden pasar inadvertidas.
- Los datos se guardan solo en el dispositivo, sin cifrado. Para uso con datos de pacientes, aplique las medidas de la Ley 1581 de 2012.
- Un software con finalidad diagnóstica o terapéutica puede considerarse dispositivo médico ante el INVIMA; defina el uso previsto y la gestión de riesgos antes de distribuirla.
- Verifique siempre dosis, contraindicaciones y disponibilidad local.

## Fuentes principales

Harrison's Principles of Internal Medicine 22.ª ed. (2025) · Nelson Textbook of Pediatrics 22.ª ed. · ADA Standards of Care in Diabetes 2026 · Guía AHA/ACC 2025 de hipertensión · GINA 2025 y GOLD 2026. Cada entidad cita además sus guías específicas.

## Licencia

Sin licencia definida: por defecto el autor conserva todos los derechos. Si desea permitir su reutilización, agregue un archivo `LICENSE` (por ejemplo MIT o CC BY-NC 4.0).
