from schemas.auth import ClientSchema

def allowADFS(client: ClientSchema):
    if client.provider in ['adfs']: return True
    else: return False

def allowLocal(client: ClientSchema):
    if client.provider in ['local']: return True
    else: return False