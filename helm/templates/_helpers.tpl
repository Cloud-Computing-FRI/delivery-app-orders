{{/*
Template helpers for the orders chart.

By default the Service name is the bare chart name ("orders"), NOT a
release-prefixed name, so the UI can address it at a stable DNS name. Set
fullnameOverride to change it.
*/}}

{{- define "orders.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "orders.fullname" -}}
{{- default (include "orders.name" .) .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "orders.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/* Common labels. Call with the root context ($). */}}
{{- define "orders.labels" -}}
helm.sh/chart: {{ include "orders.chart" . }}
app.kubernetes.io/part-of: delivery-app
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/* Selector labels. Call with the root context ($). */}}
{{- define "orders.selectorLabels" -}}
app.kubernetes.io/name: {{ include "orders.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: orders
{{- end -}}

{{/* Host of the database: the in-cluster service unless database.host overrides it. */}}
{{- define "orders.dbHost" -}}
{{- if .Values.database.host -}}
{{- .Values.database.host -}}
{{- else -}}
{{- printf "%s-db" (include "orders.fullname" .) -}}
{{- end -}}
{{- end -}}

{{/* Name of the Secret holding DATABASE_URL (pre-created one in prod). */}}
{{- define "orders.dbSecret" -}}
{{- default (printf "%s-db" (include "orders.fullname" .)) .Values.database.existingSecret -}}
{{- end -}}
