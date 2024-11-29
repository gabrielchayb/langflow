# Note: Replace **<YOUR_APPLICATION_TOKEN>** with your actual Application token

import argparse
import json
from argparse import RawTextHelpFormatter
import requests
from typing import Optional
import warnings
try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "896458c4-6091-4af5-973b-60d593fed709"
FLOW_ID = "f3cfe31c-55b6-471a-ace0-8445408a0178"
APPLICATION_TOKEN = "AstraCS:PRHmGndngbbZDwPJKsrZdKTP:150c91bdd65f19667b142882093241aa94a329a32c050af3e388db374e598d7a"
ENDPOINT = "" # You can set a specific endpoint name in the flow settings

# Você pode ajustar o fluxo adicionando um dicionário de ajustes
# ex: {"OpenAI-XXXXX": {"model_name": "gpt-4"}}
TWEAKS = {
  "ChatInput-wMp9W": {},
  "ChatOutput-e8DVl": {},
  "Prompt-DD9qG": {},
  "QdrantVectorStoreComponent-9P668": {},
  "File-sMw64": {},
  "SplitText-WjIIx": {},
  "QdrantVectorStoreComponent-dpbjU": {},
  "ParseData-bfVkx": {},
  "TextEmbedderComponent-nEGkI": {},
  "GroqModel-MHc8j": {},
  "HuggingFaceInferenceAPIEmbeddings-3clsZ": {},
  "HuggingFaceInferenceAPIEmbeddings-vXXlv": {},
  "Memory-MVbLs": {},
  "StoreMessage-a5D6v": {}
}

def run_flow(message: str,
             endpoint: str,
             output_type: str = "chat",
             input_type: str = "chat",
             tweaks: Optional[dict] = None,
             application_token: Optional[str] = None) -> dict:
    """
    Executa um fluxo com uma mensagem fornecida e ajustes opcionais.

    :param message: A mensagem a ser enviada para o fluxo
    :param endpoint: O ID ou o nome do endpoint do fluxo
    :param tweaks: Ajustes opcionais para customizar o fluxo
    :return: O JSON de resposta do fluxo
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if application_token:
        headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

def extract_response_text(response: dict) -> str:
    """
    Extrai o texto da resposta do JSON retornado pelo fluxo.
    
    :param response: O JSON de resposta do fluxo
    :return: O texto da resposta ou uma mensagem padrão se não encontrado
    """
    try:
        outputs = response.get("outputs", [])
        for output in outputs:
            messages = output.get("outputs", [])
            for message in messages:
                text = message.get("results", {}).get("message", {}).get("data", {}).get("text", "Texto não encontrado.")
                return text
    except Exception as e:
        return f"Erro ao processar a resposta: {e}"
    return "Resposta não encontrada."

def main():
    parser = argparse.ArgumentParser(description="""Execute um fluxo com uma ou múltiplas mensagens a partir de um arquivo JSON.
Forneça um arquivo JSON contendo uma lista de mensagens para enviar ao fluxo.
Execute da seguinte forma: python lang_api.py --messages_file "messages.json" --endpoint "seu_endpoint" --tweaks '{"chave": "valor"}'""",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument("--messages_file", type=str, help="Caminho para um arquivo JSON com mensagens", default=None)
    parser.add_argument("--message", type=str, help="Uma única mensagem para enviar ao fluxo", default=None)
    parser.add_argument("--endpoint", type=str, default=ENDPOINT or FLOW_ID, help="O ID ou o nome do endpoint do fluxo")
    parser.add_argument("--tweaks", type=str, help="String JSON representando os ajustes para customizar o fluxo", default=json.dumps(TWEAKS))
    parser.add_argument("--application_token", type=str, default=APPLICATION_TOKEN, help="Token da aplicação para autenticação")
    parser.add_argument("--output_type", type=str, default="chat", help="O tipo de saída")
    parser.add_argument("--input_type", type=str, default="chat", help="O tipo de entrada")
    parser.add_argument("--upload_file", type=str, help="Caminho para o arquivo a ser enviado", default=None)
    parser.add_argument("--components", type=str, help="Componentes para enviar o arquivo", default=None)

    args = parser.parse_args()
    try:
        tweaks = json.loads(args.tweaks)
    except json.JSONDecodeError:
        raise ValueError("String JSON de ajustes inválida")

    # Carregar mensagens
    messages = []
    if args.message:
        messages = [args.message]
    elif args.messages_file:
        try:
            with open(args.messages_file, "r") as f:
                messages = json.load(f)
                if not isinstance(messages, list):
                    raise ValueError("O arquivo JSON deve conter uma lista de mensagens.")
        except Exception as e:
            raise ValueError(f"Erro ao ler mensagens do arquivo: {e}")
    else:
        raise ValueError("Nenhuma mensagem fornecida. Use --message ou --messages_file para especificar a entrada.")

    # Se upload_file for fornecido, faça o upload
    if args.upload_file:
        if not upload_file:
            raise ImportError("Langflow não está instalado. Por favor, instale-o para usar a função upload_file.")
        elif not args.components:
            raise ValueError("Você precisa fornecer os componentes para enviar o arquivo.")
        tweaks = upload_file(file_path=args.upload_file, host=BASE_API_URL, flow_id=args.endpoint, components=args.components, tweaks=tweaks)

    # Processar cada mensagem
    for message in messages:
        response = run_flow(
            message=message,
            endpoint=args.endpoint,
            output_type=args.output_type,
            input_type=args.input_type,
            tweaks=tweaks,
            application_token=args.application_token
        )
        extracted_text = extract_response_text(response)
        print(f"Mensagem: {message}")
        print("Resposta do modelo:")
        print(extracted_text)
        print("-" * 80)

if __name__ == "__main__":
    main()
