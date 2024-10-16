from pydantic import BaseModel
from typing import Any, Dict

#CHALLENGE
class BiometricChallengeSchemaResponse(BaseModel):
    timeout: int
    rpId: str
    challenge: str

#REGISTER
class BiometricRegisterCredentialResponseSchema(BaseModel):
    attestationObject: str
    clientDataJSON: str

class BiometricRegisterCredentialSchema(BaseModel):
    id: str
    rawId: str
    response: BiometricRegisterCredentialResponseSchema
    type: str

class BiometricRegisterSchema(BaseModel):
    credential: BiometricRegisterCredentialSchema
    challenge: str

#LOGIN
class BiometricLoginCredentialResponseSchema(BaseModel):
    authenticatorData: str
    clientDataJSON: str
    signature: str
    userHandle: str

class BiometricLoginCredentialSchema(BaseModel):
    authenticatorAttachment: str
    clientExtensionResults: dict
    id: str
    rawId: str
    response: BiometricLoginCredentialResponseSchema
    type: str

class BiometricLoginSchema(BaseModel):
    credential: BiometricLoginCredentialSchema
    challenge: str