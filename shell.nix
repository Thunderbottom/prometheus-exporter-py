let
  pkgs = import <nixpkgs> {};
in
  pkgs.mkShell {
    name = "prometheus-exporter-env";
    buildInputs = with pkgs; [
    # basic python dependencies
    python38
    python38Packages.prometheus_client
    python38Packages.flask
  ];
  shellHook = ''
  '';
}
