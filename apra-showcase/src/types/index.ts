export type DefenseMethod = "apra" | "avg" | "clip" | "deepsight" | "foolsgold" | "rflbat";
export type AttackMethod = "a3fl" | "doba" | "neurotoxin" | "reba" | "modelreplace";

export const DEFENSE_METHODS: DefenseMethod[] = ["apra", "avg", "clip", "deepsight", "foolsgold", "rflbat"];
export const ATTACK_METHODS: AttackMethod[] = ["a3fl", "doba", "neurotoxin", "reba"];

export const DEFENSE_LABELS: Record<DefenseMethod, string> = {
  apra: "APRA",
  avg: "FedAvg",
  clip: "Clip",
  deepsight: "DeepSight",
  foolsgold: "FoolsGold",
  rflbat: "RFLBAT",
};

export const ATTACK_LABELS: Record<AttackMethod, string> = {
  a3fl: "A3FL",
  doba: "DOBA",
  neurotoxin: "Neurotoxin",
  reba: "ReBA",
  modelreplace: "ModelReplace",
};

export interface MethodResult {
  asr: number;
  accuracy: number;
}

export interface SummaryData {
  [defense: string]: {
    [attack: string]: MethodResult;
  };
}

export interface AccuracyRow {
  epoch: number;
  test_acc: number;
  bkd_acc: number;
  test_loss: number;
  bkd_loss: number;
  lr?: number;
}

export interface ApraClientTraceRow {
  epoch: number;
  client_id: number;
  role: "malicious" | "benign";
  is_adversary: number;
  update_norm: number;
  mad_z_score: number;
  mad_pass: number;
  mad_effective_pass: number;
  cluster_label: number;
  selected_cluster: number;
  cluster_pass: number;
  cluster_effective_pass: number;
  final_selected: number;
  trust_weight: number;
  clip_factor: number;
}

export interface ApraRoundSummaryRow {
  epoch: number;
  num_sampled: number;
  num_adversaries: number;
  mad_pass_ids: string;
  mad_reject_ids: string;
  mad_k: number;
  mad_safety_keep_used: number;
  cluster_best_k: number;
  cluster_selected_cluster: number;
  cluster_pass_ids: string;
  cluster_reject_ids: string;
  final_selected_ids: string;
  final_rejected_ids: string;
  final_selected_benign_count: number;
  final_selected_malicious_count: number;
}

export interface ReplayFrame {
  roundSummary: ApraRoundSummaryRow;
  clientTraces: ApraClientTraceRow[];
}
