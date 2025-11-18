import { createClient, SupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://kxqhklgknwgmehyyttzp.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt4cWhrbGdrbndnbWVoeXl0dHpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMzMjAzNDUsImV4cCI6MjA3ODk2MzQ1fQ.efpywMHQ-lb3HX27gxxkBuojDIytHrwasoJsiOB66m4';

export const supabase: SupabaseClient = createClient(supabaseUrl, supabaseAnonKey);

