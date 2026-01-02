# Building The Add-On for Testing


Clone this repo:
```
git clone https://github.com/beanwareHQ/beantextures/
```

Then, if you use *nix, simply run the `build.sh` executable from this repo to get the working add-on zip file. Otherwise, execute this manually:
```
blender --command extension build --source-dir beantextures --output-dir .
```

Alternatively, to make and test changes quickly, you can symbolic link (or shortcut) the `beantextures` directory directly to Blender's extensions folder. For example:
```
ln -s ~/path/to/beantextures-git ~/.config/blender/5.0/extensions/user_default/beantextures
```



# Reporting Issues
Make sure that the issue you found persists in the development version of the add-on (i.e latest code from the `main` branch). Once confirmed, please report it [to this issues page](https://github.com/BeanwareHQ/beantextures/issues).

# PRs
PRs to this project are welcomed. Fixes will be merged after review. If your PR is not a bug fix, please open a discussion first or mail me at [daringcuteseal@gmail.com](mailto:daringcuteseal@gmail.com).
