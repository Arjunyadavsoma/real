{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.flask
    pkgs.python311Packages.sqlalchemy
    pkgs.python311Packages.flask_login
    pkgs.python311Packages.flask_migrate
    pkgs.python311Packages.flask_wtf
    pkgs.python311Packages.pillow
  ];
}
