# 🛡️ SUITE DE SEGURIDAD Y BLINDAJE MILITAR - RODRIGUEZ LAWNCARE

Este folder implementa la suite de defensa cliente-servidor más avanzada del mercado contra piratería web, clonación de proyectos, manipulación de marcas, ataques de fuerza bruta y robo de código.

---

## ⚡ MATRIZ DE DEFENSA ACTIVA (100% INVISIBLE PARA CLIENTES)

Tu sitio web está protegido por **8 capas simultáneas** que operan en segundo plano sin mostrar ninguna alerta ni alterar la experiencia visual de tus clientes:

### 1. 🧬 Trampa Anti-Depuración y Anti-Crackers (Debugger Trap)
- **Tecnología:** Medición de latencia de ejecución (`performance.now()`) y detección de dimensiones de ventana.
- **Acción:** Si un pirata informático intenta adjuntar un depurador (breakpoints) o inspeccionar la memoria en vivo de tu web, la ejecución detecta el pico de latencia y **deshabilita la consola y borra los registros (`console.clear()`)**, impidiendo la ingeniería inversa.

### 2. 🧊 Congelamiento de Prototipos (Anti-Prototype Pollution)
- **Tecnología:** `Object.freeze(Object.prototype)` y `Object.freeze(Array.prototype)`.
- **Acción:** Impide que scripts inyectados o extensiones de navegador sobreescriban las funciones nativas de JavaScript.
- **Bloqueo de Inyección:** Se anuló la ejecución de `eval()` dinámico y `document.write` para prevenir ataques de DOM Clobbering.

### 3. 🛡️ Auto-Sanación de Marca y Enlaces (Self-Healing DOM Engine)
- **Tecnología:** `MutationObserver` profundo con vigilancia de subárbol, atributos y texto.
- **Acción:** Si alguien intenta mediante código cambiar:
  - El nombre de tu negocio: **RODRIGUEZ LAWNCARE**
  - El teléfono de tu IA: **(254) 852-8163**
  - Tu WhatsApp directo: **(254) 612-1399**
  - Tu correo personal: **arizmendir754@gmail.com**
  El motor lo detecta en microsegundos y **restituye tus datos oficiales al instante**.
  Cualquier `<script>` o `<iframe>` no autorizado que intente insertarse en el DOM es **eliminado en tiempo real**.

### 4. 🚫 Bloqueo Anti-Extracción de Código y Assets
- **Clic Derecho Neutralizado:** Menús contextuales de inspección bloqueados en toda la web.
- **Teclas Piratas Desactivadas:**
  - `F12` (Consola / DevTools).
  - `Ctrl + Shift + I` / `Ctrl + Shift + J` / `Ctrl + Shift + C` (Inspección).
  - `Ctrl + U` (Ver código fuente HTML).
  - `Ctrl + S` (Guardar página completa).
  - `Ctrl + P` (Volcar diseño a PDF).
- **Anti-Arrastre de Medios:** Las imágenes tienen `user-drag: none` para que nadie pueda arrastrarlas a su escritorio.
- **Anti-Scraping de Texto:** `user-select: none` global para evitar copia y raspado automatizado de contenido.

### 5. 🍯 Trampa Invisible Anti-Bots (Honeypot + Time Guard)
- **Tecnología:** `security/anti-bot.js`
- **Honeypot Oculto:** Crea campos trampa invisibles para humanos. Los bots automatizados los llenan solos y el sistema descarta su petición en silencio.
- **Velocidad Humana:** Si un script envía un formulario en menos de 1.4 segundos desde que cargó la web, lo bloquea por comportamiento no humano.
- **Rate-Limiting:** Evita envíos masivos y spam con un enfriamiento estricto de 3.5 segundos entre clics.

### 6. 🧹 Limpiador Anti-Inyección de Tokens y Payloads (XSS Scrubber)
- Monitorea todo texto que entre a formularios y elimina en tiempo real:
  - Tokens JWT (`eyJ...`)
  - Tokens de autenticación (`Bearer ...`)
  - Llaves API (`sk-...`, `ghp_...`)
  - Payloads maliciosos (`<script>`, `javascript:`, `onerror=`, `document.cookie`)

### 7. 🪟 Blindaje contra Clonación en Iframes (Anti-Clickjacking)
- Si otro dominio intenta cargar tu página dentro de un marco para engañar a tus clientes, el navegador rompe el marco y regresa a tu dominio (`window.top.location = window.self.location`).

### 8. 🖨️ Neutralizador de Impresión y Copiado a PDF
- Si intentan imprimir tu sitio o guardarlo como PDF desde el menú del navegador, las reglas de impresión (`@media print`) ocultan la estructura para que no puedan clonar los gráficos.

---

## 📂 Archivos del Sistema de Seguridad:
- **`security/web-shield.js`**: Blindaje de ejecución, anti-debug, auto-sanación del DOM y limpiador de tokens.
- **`security/anti-bot.js`**: Trampas honeypot, control de tiempo y limitador de velocidad contra bots.
- **`security/security.css`**: Reglas silenciosas anti-arrastre, anti-copia y neutralizador de PDF.
- **`security/README.md`**: Documentación técnica del sistema.
