VERSION=42

sed -i 's/2.10.[0-9]\+/2.10.'$VERSION'/g' Dockerfile.qa
docker build . -f Dockerfile.base -t gcr.io/engaged-ground-343617/givesomeapp:2.10-base
docker build . -f Dockerfile.live -t gcr.io/engaged-ground-343617/givesomeapp:2.10.${VERSION}
docker build . -f Dockerfile.qa -t gcr.io/engaged-ground-343617/givesomeapp:2.10.${VERSION}-qa
docker push gcr.io/engaged-ground-343617/givesomeapp:2.10.${VERSION}-qa
docker push gcr.io/engaged-ground-343617/givesomeapp:2.10.${VERSION}
