#py2applet --make-setup learningenglish.py;
python setup.py py2app;
cp -R ../Learning-English/Units dist/learningenglish.app/Contents/Resources/;
cp -R ../Learning-English/icons dist/learningenglish.app/Contents/Resources/;
cp -R ../Learning-English/extras dist/learningenglish.app/Contents/Resources/;
cp -R ../Learning-English/sounds dist/learningenglish.app/Contents/Resources/;
cp -R ../Learning-English/include dist/learningenglish.app/Contents/Resources/;
