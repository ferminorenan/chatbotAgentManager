import requests

def send_mensage_whatsapp(token, tell_id, tell_to, mensage):
    url = f"https://graph.facebook.com/v13.0/{tell_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": tell_to,
        "type": "text",
        "text": {
            "body": mensage
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return {"response":"Mensagem enviada com sucesso!"}
    else:
        return {"error":f"Erro ao enviar mensagem: {response.status_code}"}