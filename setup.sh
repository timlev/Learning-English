#py2applet --make-setup rosettatablet.py;
python setup.py py2app;
cp -R ../rosetta-tablet/Units dist/rosettatablet.app/Contents/Resources/;
cp -R ../rosetta-tablet/icons dist/rosettatablet.app/Contents/Resources/;
cp -R ../rosetta-tablet/extras dist/rosettatablet.app/Contents/Resources/;
cp -R ../rosetta-tablet/sounds dist/rosettatablet.app/Contents/Resources/;
cp -R ../rosetta-tablet/include dist/rosettatablet.app/Contents/Resources/;
