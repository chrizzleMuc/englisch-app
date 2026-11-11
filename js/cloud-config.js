// Zugang zum Online-Speicher (Supabase). Beides darf öffentlich sein:
// Der "publishable"/"anon"-Schlüssel erlaubt nur, was die Regeln in der Datenbank zulassen,
// und jede Familie sieht nur ihre eigenen Daten (Anmeldung per E-Mail).
// Leer = Online-Speicherung ist nicht eingerichtet, die App speichert nur auf dem Gerät.
export const SUPABASE_URL = "";
export const SUPABASE_KEY = "";
