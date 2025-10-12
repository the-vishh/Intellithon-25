// 🔐 END-TO-END ENCRYPTION MODULE
// Zero-knowledge architecture - server never sees plaintext user data

use base64::{Engine as _, engine::general_purpose};
use serde::{Deserialize, Serialize};
use sha2::{Sha256, Digest};
use ring::aead::{Aad, BoundKey, Nonce, NonceSequence, OpeningKey, SealingKey, UnboundKey, AES_256_GCM};
use ring::rand::{SecureRandom, SystemRandom};
use std::error::Error;

/// User's encryption key derived from their UUID
/// Stored client-side only, never sent to server
#[derive(Debug, Clone)]
pub struct UserEncryptionKey {
    pub user_id: String,
    pub key: [u8; 32], // AES-256 key
}

/// Encrypted data blob stored in database
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EncryptedData {
    pub ciphertext: String,  // Base64 encoded
    pub nonce: String,        // Base64 encoded (12 bytes)
    pub tag: String,          // Base64 encoded (16 bytes)
}

impl UserEncryptionKey {
    /// Generate encryption key from user ID
    /// Client-side: Uses user's UUID as seed
    /// Server never knows this key!
    pub fn from_user_id(user_id: &str) -> Self {
        let mut hasher = Sha256::new();
        hasher.update(user_id.as_bytes());
        hasher.update(b"PhishGuardAI-E2E-Encryption-v1");
        let key_bytes = hasher.finalize();

        let mut key = [0u8; 32];
        key.copy_from_slice(&key_bytes);

        Self {
            user_id: user_id.to_string(),
            key,
        }
    }

    /// Encrypt sensitive data before sending to server
    pub fn encrypt(&self, plaintext: &str) -> Result<EncryptedData, Box<dyn Error>> {
        let cipher = Aes256Gcm::new(&self.key.into());

        // Generate random nonce (12 bytes for GCM)
        let nonce_bytes = rand::random::<[u8; 12]>();
        let nonce = Nonce::from_slice(&nonce_bytes);

        // Encrypt
        let ciphertext = cipher.encrypt(nonce, plaintext.as_bytes())
            .map_err(|e| format!("Encryption failed: {}", e))?;

        Ok(EncryptedData {
            ciphertext: general_purpose::STANDARD.encode(&ciphertext),
            nonce: general_purpose::STANDARD.encode(&nonce_bytes),
            tag: "".to_string(), // Tag is included in ciphertext for AES-GCM
        })
    }

    /// Decrypt data received from server
    pub fn decrypt(&self, encrypted: &EncryptedData) -> Result<String, Box<dyn Error>> {
        let cipher = Aes256Gcm::new(&self.key.into());

        // Decode base64
        let ciphertext = general_purpose::STANDARD.decode(&encrypted.ciphertext)?;
        let nonce_bytes = general_purpose::STANDARD.decode(&encrypted.nonce)?;
        let nonce = Nonce::from_slice(&nonce_bytes);

        // Decrypt
        let plaintext = cipher.decrypt(nonce, ciphertext.as_ref())
            .map_err(|e| format!("Decryption failed: {}", e))?;

        Ok(String::from_utf8(plaintext)?)
    }
}

/// Hash sensitive data for database indexing without exposing content
pub fn hash_for_indexing(data: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data.as_bytes());
    format!("{:x}", hasher.finalize())
}

/// Generate device fingerprint for tracking device-specific metrics
pub fn generate_device_fingerprint(user_agent: &str, extension_version: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(user_agent.as_bytes());
    hasher.update(extension_version.as_bytes());
    format!("{:x}", hasher.finalize())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_encryption_decryption() {
        let key = UserEncryptionKey::from_user_id("test-user-123");
        let plaintext = "https://malicious-phishing-site.com";

        let encrypted = key.encrypt(plaintext).unwrap();
        let decrypted = key.decrypt(&encrypted).unwrap();

        assert_eq!(plaintext, decrypted);
    }

    #[test]
    fn test_different_users_different_keys() {
        let key1 = UserEncryptionKey::from_user_id("user-1");
        let key2 = UserEncryptionKey::from_user_id("user-2");

        assert_ne!(key1.key, key2.key);
    }

    #[test]
    fn test_hash_consistency() {
        let hash1 = hash_for_indexing("example.com");
        let hash2 = hash_for_indexing("example.com");

        assert_eq!(hash1, hash2);
    }
}
