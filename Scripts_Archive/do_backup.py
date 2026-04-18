import os, shutil, datetime

base = r'c:\Users\Administrator\Desktop\111'
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
bdir = os.path.join(base, f'backup_final_{ts}')
os.makedirs(bdir+'/js', exist_ok=True)
os.makedirs(bdir+'/css', exist_ok=True)
shutil.copy(os.path.join(base, 'js/main.js'), bdir+'/js/main.js')
shutil.copy(os.path.join(base, 'index.html'), bdir+'/index.html')
for f in os.listdir(os.path.join(base, 'css')):
    shutil.copy(os.path.join(base, 'css', f), os.path.join(bdir, 'css', f))
print('Backup done:', bdir)
