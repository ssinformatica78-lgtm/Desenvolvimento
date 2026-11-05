# Entrega privada — House TV 6.5.7 / 792

Os arquivos binários desta branch são um pacote **cifrado**, não fontes públicos.
A senha de transferência é fornecida somente ao destinatário na conversa.
Não é a senha do servidor, do login do aplicativo ou da chave de assinatura.

Baixe o ZIP desta branch e extraia os arquivos na VPS, em uma pasta privada.
Execute `python3 receber-pacote.py` e informe a senha de transferência.
São necessários Python 3 e OpenSSL. O script autentica o pacote antes de decifrar
e verifica o SHA-256 do arquivo original. Não instala, assina nem publica APK.

O resultado é `House-TV-6.5.7-pacote-VPS.tar.gz`. Esse arquivo contém o candidato
SEM ASSINATURA, os fontes de revisão, o plano de testes e os scripts para usar
exclusivamente a chave original na VPS. Não substituir o APK oficial.
