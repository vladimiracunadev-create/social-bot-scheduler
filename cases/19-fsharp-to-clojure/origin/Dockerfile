# Emisor F# (Case 19) — build .NET; se ejecuta bajo demanda.
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY Publisher.fsproj ./
RUN dotnet restore
COPY Publisher.fs posts.json ./
RUN dotnet publish -c Release -o /app

FROM mcr.microsoft.com/dotnet/runtime:9.0
WORKDIR /app
COPY --from=build /app ./
COPY --from=build /src/posts.json ./posts.json
CMD ["dotnet", "Publisher.dll"]
