[app]

title = SistemaAtelie
package.name = sistemadoatelie
package.domain = org.atelie

# Código fonte — inclui TUDO
source.dir = .
source.include_exts = py, kv, png, jpg, jpeg, json

requirements = python3, kivy, kivymd, pillow, requests, mysql-connector-python

# Android API
android.api = 33
android.minapi = 21
android.ndk = 25b

# Tela
fullscreen = 0
orientation = portrait

# Permissões
android.permissions = INTERNET, ACCESS_NETWORK_STATE, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# Permite HTTP sem SSL
android.allow-cleartext = 1

# Debug
log_level = 2
