export type RoleKey =
  | "organizer"
  | "developer"
  | "resident"
  | "professional"
  | "admin";

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Role {
  id: number;
  name: RoleKey | string;
  description?: string | null;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  organization_name?: string | null;
  is_active: boolean;
  roles: Role[];
  created_at: string;
}

export interface Unit {
  id: number;
  project_id: number;
  unit_number: string;
  floor?: number | null;
  existing_area_sqm?: number | null;
  residents_count: number;
}

export interface Project {
  id: number;
  name: string;
  city: string;
  address?: string | null;
  description?: string | null;
  owner_id: number;
  current_stage: string;
  developer_payment_required: boolean;
  per_unit_price_ils: number;
  is_active: boolean;
  created_at: string;
  units: Unit[];
}

export interface Resident {
  id: number;
  project_id: number;
  unit_id?: number | null;
  full_name: string;
  phone?: string | null;
  email?: string | null;
  is_primary_contact: boolean;
  consent_status: string;
}

export interface Signature {
  id: number;
  project_id: number;
  resident_id: number;
  signature_provider: string;
  external_reference?: string | null;
  status: string;
  signed_at?: string | null;
}

export interface WorkflowStage {
  id: number;
  project_id: number;
  stage_key: string;
  status: string;
  started_at?: string | null;
  completed_at?: string | null;
  notes?: string | null;
}

export interface DeveloperBid {
  id: number;
  project_id: number;
  developer_name: string;
  proposal_summary?: string | null;
  score?: number | null;
  price_offer_ils?: number | null;
  status: string;
}

export interface Plan {
  id: number;
  project_id: number;
  name: string;
  zoning_status: string;
  feasibility_score?: number | null;
  assumptions_json?: string | null;
}

export interface DocumentItem {
  id: number;
  project_id: number;
  title: string;
  category: string;
  storage_key: string;
  mime_type?: string | null;
  visibility: string;
  metadata_json?: string | null;
}

export interface MessageItem {
  id: number;
  project_id: number;
  sender_id: number;
  channel: string;
  recipient: string;
  body: string;
  delivery_status: string;
  external_message_id?: string | null;
}

export interface BillingPlan {
  id: number;
  code: string;
  name: string;
  plan_type: string;
  monthly_price_ils: number;
  per_unit_price_ils: number;
  included_features_json?: string | null;
  is_active: boolean;
}

export interface Subscription {
  id: number;
  billing_plan_id: number;
  user_id?: number | null;
  project_id?: number | null;
  status: string;
  started_at: string;
  ends_at?: string | null;
  auto_renew: boolean;
  add_ons_json?: string | null;
}

export interface Invoice {
  id: number;
  subscription_id: number;
  amount_ils: number;
  currency: string;
  status: string;
  issued_at: string;
  due_at?: string | null;
  paid_at?: string | null;
  line_items_json?: string | null;
}

export interface ProjectCostEstimate {
  project_id: number;
  unit_count: number;
  per_unit_price_ils: number;
  estimated_total_ils: number;
}

