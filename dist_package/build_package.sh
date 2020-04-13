#!/bin/bash

# main function
main() {

  usage=false
  wheel=false
  debian=false

  while [[ $# -gt 0 ]]
  do
    case "$1" in
        "--help" ) usage=true; shift;;
        "--wheel" ) wheel=true; shift;;
        "--debian" ) debian=true; shift;;
  esac
  done

  # change to root directory
  cd ../

  # set version from __init__.py file
  set_version

  if [[ "$usage" = true ]]; then print_usage; fi
  if [[ "$wheel" = true ]]; then build_wheel; fi
  if [[ "$debian" = true ]]; then build_debian; fi
}

print_usage() {

  echo ""
  echo "Usage:     build_package.sh [--help] [--wheel] [--debian]"
  echo ""
  echo "--wheel    builds the python wheel package for pip installation"
  echo ""
  echo "--debian   build the debian package for ubuntu/debian distros"
  echo ""
  exit 1
}

build_wheel() {

  echo -e "Build python wheel file\n"
  build_wheel_file
  move_wheel_file
  remove_setup_dist_files

}

build_debian() {

  echo -e "Build debian package\n"
  build_wheel_file
  move_wheel_file_deb
  cp_config_file
  cp_service_file
  remove_setup_dist_files
  build_deb_package
  remove_etc_folder

}

# set the app version
set_version() {

  version_file=ComunioScore/__init__.py
  APP_VERSION="$( cat ${version_file} | grep '__version_info__ =' | sed 's/__version_info__ =//')"
  app_without_char=${APP_VERSION//[()\']/}
  app_no_whitespace="$(echo -e "${app_without_char}" | tr -d '[:space:]')"
  app_vers="$(echo -e "${app_no_whitespace}" | tr , .)"
  echo "Set version to " $app_vers
  sed -i "s/Version: .*/Version: $app_vers/g" dist_package/ComunioScore_deb/DEBIAN/control

}

# build the whl file
build_wheel_file(){

  sudo python3 setup.py bdist_wheel

}

move_wheel_file() {

  cp dist/ComunioScore-*-py3-none-any.whl dist_package/

}

move_wheel_file_deb() {

  mkdir -p dist_package/ComunioScore_deb/etc/ComunioScore/
  cp dist/ComunioScore-*-py3-none-any.whl dist_package/ComunioScore_deb/etc/ComunioScore

}

cp_config_file() {

  mkdir -p dist_package/ComunioScore_deb/etc/ComunioScore/
  cp ComunioScore/config/comunioscore.ini dist_package/ComunioScore_deb/etc/ComunioScore/

}

cp_service_file() {

  mkdir -p dist_package/ComunioScore_deb/etc/systemd/system/
  cp service/ComunioScore.service dist_package/ComunioScore_deb/etc/systemd/system/

}

remove_setup_dist_files() {

  sudo rm -r dist/ build/ ComunioScore.egg-info

}

build_deb_package() {

  dpkg -b dist_package/ComunioScore_deb/ dist_package/ComunioScore_$app_vers.deb

}

remove_etc_folder() {

  sudo rm -r dist_package/ComunioScore_deb/etc/

}

main "$@"
