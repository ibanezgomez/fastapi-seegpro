from schemas.user import UserSchemaPartialUpdate
from services.base import BaseService
from services.user import UserDataManager
from services.auth import AuthService, TOKEN_TYPE
from schemas.base import SuccessResponse
from schemas.auth import TokenSchema
from schemas.biometric import *
from utils.exceptions import CustomException
from utils.logger import log
from fido2.server import Fido2Server
from fido2.webauthn import *
from fido2.features import webauthn_json_mapping
from fido2.utils import websafe_encode, websafe_decode
import base64
from fastapi import Response

rp = PublicKeyCredentialRpEntity("localhost", "localhost")
not_verify_origin = lambda x: True
fido2_server = Fido2Server(rp, verify_origin=not_verify_origin)
webauthn_json_mapping.enabled = True
CHALLENGE_TIMEOUT = 60000

class BiometricService(BaseService):
    @BaseService.HTTPExceptionHandler
    @BaseService.IsAuthenticated
    def get_biometric_challenge(self) -> BiometricChallengeSchemaResponse | None:
        user_id = self.auth.user.id
        user = UserDataManager(self.session).get_user(id=user_id)

        if not user:
            log.error(action="[get_biometric_challenge]", message=f"User does not exist")
            raise CustomException("User does not exist", None, 404)
        
        try:
            challenge_options, _ = fido2_server.register_begin(
                PublicKeyCredentialUserEntity(
                    id=user_id.encode('utf-8'),
                    name=self.auth.user.name,
                    display_name=self.auth.user.name,
                )
            )

            challenge_base64 = base64.b64encode(challenge_options.public_key.challenge).decode("utf-8")
            
            result = {
                "timeout": CHALLENGE_TIMEOUT,
                "rpId": challenge_options.public_key.rp.id,
                "challenge": challenge_base64
            }
        except Exception as e:
            log.error(action="[get_biometric_challenge]", message=f"There was an error generating FIDO2 challenge. Exception: {e}")
            raise CustomException("There was an error generating FIDO2 challenge", None, 400)

        data = UserSchemaPartialUpdate(biometric_challenge=challenge_base64)
        if UserDataManager(self.session).update_partial_user(user_id, data):
            return BiometricChallengeSchemaResponse(**result)
        else:
            log.error(action="[get_biometric_challenge]", message=f"There was an error storing FIDO2 challenge")
            raise CustomException("There was an error storing FIDO2 challenge", None, 400)

    @BaseService.HTTPExceptionHandler
    @BaseService.IsAuthenticated
    def register_biometric(self, biometric_data: BiometricRegisterSchema):
        user_id = self.auth.user.id
        user = UserDataManager(self.session).get_user(id=user_id)

        if not user:
            log.error(action="[register_biometric]", message=f"User does not exist")
            raise CustomException("User does not exist", None, 404)

        if not user.biometric_challenge:
            log.error(action="[register_biometric]", message=f"User has not generated biometric challenge")
            raise CustomException("User has not generated biometric challenge", None, 404)

        try:
            register: AuthenticatorData = fido2_server.register_complete(
                state={
                    "challenge": user.biometric_challenge,
                    "user_verification": None
                },
                response=RegistrationResponse(
                    id=websafe_decode(biometric_data.credential.id),
                    response=AuthenticatorAttestationResponse(
                        client_data=CollectedClientData(
                            websafe_decode(biometric_data.credential.response.clientDataJSON)
                        ),
                        attestation_object=AttestationObject(
                            websafe_decode(biometric_data.credential.response.attestationObject)
                        )
                    )
                )
            )
        except Exception as e:
            log.error(action="[register_biometric]", message=f"There was an error registering FIDO2 credentials. Exception: {e}")
            raise CustomException("There was an error registering FIDO2 credentials", None, 400)

        data = UserSchemaPartialUpdate(biometric_credential=websafe_encode(register.credential_data))
        if UserDataManager(self.session).update_partial_user(user_id, data):
            return SuccessResponse(data={"status":"Biometric registered"})
        else:
            log.error(action="[register_biometric]", message=f"There was an error storing FIDO2 credentials")
            raise CustomException("There was an error storing FIDO2 credentials", None, 400)

    @BaseService.HTTPExceptionHandler
    def login_biometric(self, response: Response, login: BiometricLoginSchema) -> TokenSchema | None:
        user = UserDataManager(self.session).get_user(biometric_challenge=login.challenge)

        if not user:
            log.error(action="[login_biometric]", message=f"Challenge does not exist")
            raise CustomException("User does not exist", None, 404)
        
        if not user.biometric_credential:
            log.error(action="[login_biometric]", message=f"User has not generated biometric credentials")
            raise CustomException("User has not generated biometric credentials", None, 404)

        try:
            fido2_server.authenticate_complete(
                state={
                    "challenge": user.biometric_challenge,
                    "user_verification": None
                },
                credentials=[
                    AttestedCredentialData(websafe_decode(user.biometric_credential))
                ],
                credential_id=websafe_decode(login.credential.id),
                client_data=CollectedClientData(
                    websafe_decode(login.credential.response.clientDataJSON)
                ),
                auth_data=AuthenticatorData(
                    websafe_decode(login.credential.response.authenticatorData)
                ),
                signature=websafe_decode(login.credential.response.signature)
            )
        except Exception as e:
            log.error(action="[login_biometric]", message=f"FIDO2 login error. Exception: {e}")
            raise CustomException("There was an error in login with FIDO2 credentials", None, 400)

        return AuthService()._create_access_token(response, user)