# Inicialización

## Asistente

Crear un archivo asistent.json en la raiz con la estructura. Si el archivo no existe definir al asistente en el archivo functions en el método create_assistant

```json
{"assistant_id": "asst_fzBGqKnmlu677u95pEMMn7YO"}
```
## Funciones tool_calls

Se encuentran en el archivo functions. Crear cada función según la definición del asistente.

# Pruebas

## Start thread
Para comenzar un hilo 

```bash
curl -X GET http://localhost:8080/start
```

## Prompt message
Luego de iniciar invocar al endpoint /message con el thread_id correspondiente

Para obtener solo latitud y longitud
```bash
curl -X POST http://localhost:8080/message \
-H "Content-Type: application/json" \
-d '{"thread_id": "thread_8JYUx4DNo6xMbYtkr2ziy86S", "message": "quiero la ubicación de barcelona"}'
```
Para obtener el clima
```bash
curl -X POST http://localhost:8080/message \
-H "Content-Type: application/json" \
-d '{"thread_id": "thread_8JYUx4DNo6xMbYtkr2ziy86S", "message": "quiero clima de barcelona"}'
```
