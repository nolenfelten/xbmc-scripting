Made with WindowXMl (Thanks Donno)
This means, you need a pretty new XBMC build.

How to get this work in progress build to work for testing:

First, build script and run.

It will ask you about master password etc, enter one if you want.

2) You will notice the only available button is settings, this is due to the XinBox buttons
   being disabled due to it detecting now Email settings have been set up (this is yet to be implemented in GUI)

3) Exit script. Open up the file settings.xib file in your XBMC/Userdata/script_data/XinBox folder

4) Now, you need to know the layout of the settings, each settings is seperated by a  "   |   "
   and the "    -    " is simply a place holder.

    no|-|mypopaddress|myusername|mypassword|-|mypopaddress2|myusername2|mypassword2|-


 the first is yes or no depending on if you have a master password on or off

 the second is the master password if one is set otherwise its a "   -   "

  the third is the pop address eg: pop.ihug.co.nz

   the fourth is the email username
   
   the fifth is the email password
 
   the sixth is if your pop server uses SSL - if not then leave these
                                            - if yes then change to your ssl port number

  OPTIONAL!! from here on

   the seventh is the pop address for a second account eg: pop.ihug.co.nz

  the eight is the email username for a second account

   the ninth is the email password  for a second account

  the tenth is if your second acount has SSL

  
  there is no "   |   " at the end of the tenth section.



 ENJOY!