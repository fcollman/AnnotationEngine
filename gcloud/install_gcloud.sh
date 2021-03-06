gcloud version || true
if [ ! -d "$HOME/google-cloud-sdk/bin" ]; then rm -rf $HOME/google-cloud-sdk; export
  CLOUDSDK_CORE_DISABLE_PROMPTS=1; curl https://sdk.cloud.google.com | bash; fi
source $HOME/google-cloud-sdk/path.bash.inc
gcloud version
gcloud components update
gcloud components install beta
gcloud components install beta cbt
