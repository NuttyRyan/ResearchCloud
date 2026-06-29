{{- define "researchcloud.labels" -}}
app.kubernetes.io/name: researchcloud
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{/*
Build a fully-qualified image reference, prefixing the global registry when set.
Usage: {{ include "researchcloud.image" (dict "image" .Values.backend.image "global" .Values.global) }}
*/}}
{{- define "researchcloud.image" -}}
{{- $registry := .global.imageRegistry | default "" -}}
{{- if $registry -}}
{{ $registry }}/{{ .image.repository }}:{{ .image.tag }}
{{- else -}}
{{ .image.repository }}:{{ .image.tag }}
{{- end -}}
{{- end -}}

{{/*
Render imagePullSecrets block from a list of {name: ...} entries.
*/}}
{{- define "researchcloud.imagePullSecrets" -}}
{{- with .Values.imagePullSecrets }}
imagePullSecrets:
{{- toYaml . | nindent 0 }}
{{- end }}
{{- end -}}

{{/*
The database URL the backend should use: the bundled Postgres service when enabled,
otherwise the externally provided URL.
*/}}
{{- define "researchcloud.databaseUrl" -}}
{{- if .Values.postgres.enabled -}}
postgresql+psycopg://{{ .Values.postgres.user }}:{{ .Values.postgres.password }}@researchcloud-postgres:5432/{{ .Values.postgres.database }}
{{- else -}}
{{ .Values.externalDatabaseUrl }}
{{- end -}}
{{- end -}}
