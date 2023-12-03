
in windows
in vsterminal i used :
set DATABASE_URL=xxx 

in app i used :/
import os
ahmed = os.environ.get('DATABASE_URL')
print("Value of 'DATABASE_URL':", ahmed)



why the output is None