# Propuesta de Mejora: Implementación del Protocolo "HackNet" en APIE
**Basado en:** OSINT Strategies (AmLL7amN8Tk)

## 1. Plan Práctico de Implementación

### Fase A: Reconocimiento de Dominios (Inspirado en TheHarvester)
Para cada prospecto SUCCESS, APIE no solo buscará el nombre, sino que intentará identificar su dominio web corporativo. 
- **Acción:** Escaneo de motores de búsqueda para hallar el dominio (ej. `empresa.com.do`).
- **Uso:** Generar el patrón de correos probable (`nombre.apellido@dominio.com`) basándonos en la estructura del dominio hallada.

### Fase B: Validación de Perfiles Reales (Inspirado en Epieos)
Una vez que obtengamos un posible correo del dorking, aplicaremos una validación de "Reverse Lookup".
- **Acción:** Verificar si ese correo está vinculado a una cuenta de Google, Skype o redes sociales sin enviar el correo todavía.
- **Uso:** Saneamiento extremo. Solo enviaremos correos a direcciones que confirmemos que pertenecen a una persona física real, no a buzones muertos.

### Fase C: Bypass de Recepción (Inspirado en ContactOut)
En lugar de apuntar a `info@` o `recepcion@`, buscaremos perfiles de Gerentes o Dueños en LinkedIn asociados a la empresa.
- **Acción:** Dorking específico: `site:linkedin.com "Gerente" OR "Owner" "Nombre de la Empresa"`.
- **Uso:** El correo se dirigirá por nombre y apellido al tomador de decisión, mencionando: *"Hola [Nombre], vimos su excelente gestión en..."*.

## 2. Cómo mejora nuestro objetivo
1. **Conversión:** Al saltar el filtro de la secretaria (`info@`) y llegar directo al gerente, la tasa de respuesta sube de un 2% a un estimado de 15-20%.
2. **Prestigio:** Un correo validado por OSINT que mencione perfiles reales demuestra que ARMULTIS no es un bot masivo, sino una empresa de inteligencia corporativa.
3. **Eficiencia de Servidor:** Evitamos rebotes (bounces) al validar la existencia real del perfil antes del envío, protegiendo la IP del `email_tool.py`.

## 3. Próximo Paso (Pendiente de Aprobación)
## 4. Validación de Propiedad de Dominio (Zero Token Strategy)
Para asegurar que un dominio pertenece realmente al RNC/Empresa sin gastar tokens:
1.  **Detección via Shadow Engine:** Usamos el motor v10.6 para extraer el link del sitio web desde los resultados de búsqueda.
2.  **Scraping de Huella Legal:** El script accede al dominio y busca mediante **Regex (Expresiones Regulares)** la existencia del RNC o el Nombre Legal en el Footer, Términos y Condiciones o Aviso Legal del sitio.
3.  **DNS Verification:** Uso del comando nativo `dig` para identificar registros TXT o SOAs que vinculen el dominio con la infraestructura de la empresa.
4.  **SMTP Handshake:** Verificación de la existencia de los correos mediante conexión directa al puerto 25 (Handshake SMTP) para confirmar si el buzón acepta mensajes, sin llegar a enviarlos.

---
**Estatus:** PLAN TÉCNICO DETALLADO (0 TOKENS)
