# wpp-fastapi

api intermediaria que conecta 

WPP -> API -> LANGFLOW 

1. criar ambiente virtual : 

```bash
python -m venv .venv
```

2. ativar ambiente virtual :

```bash
source .venv/bin/activate
``` 

windows: 

```bash
.venv\Scripts\Activate.ps1
``` 

3. instalar dependencias

```bash
pip install -r requirements.txt
```

4. rodar main.py: 

```bash
fastapi dev main.py
```

5. testar langflow fluxo 

```bash
python lang_api.py "oi"                                                      
```

mas apenas python lang_api.py "Sua mensagem vai aqui" resolve! oioi


7. testar langflow fluxo com varias mensagens

```bash
python lang_api.py --messages_file messages.json                                                  
```-
.
