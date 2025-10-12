// 🔐 SIMPLIFIED ENCRYPTION MODULE
// For production, use this simpler approach

use serde::{Deserialize, Serialize};
use sha2::{Sha256, Digest};

/// Hash a string for indexing (without revealing plaintext)
pub fn hash_for_indexing(data: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data.as_bytes());
    format!("{:x}", hasher.finalize())
}

/// Simple encryption structure (encryption happens client-side)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EncryptedData {
    pub ciphertext: String,
    pub nonce: String,
}

impl EncryptedData {
    pub fn new(ciphertext: String, nonce: String) -> Self {
        Self { ciphertext, nonce }
    }
}

/// User encryption key (only metadata, actual key derived client-side)
pub struct UserEncryptionKey {
    pub user_id: String,
}

impl UserEncryptionKey {
    pub fn new(user_id: String) -> Self {
        Self { user_id }
    }
}
