import bcrypt from "bcrypt";

const SALT_ROUNDS = 10;

async function hashPassword(password) {
  const hashed = await bcrypt.hash(password, SALT_ROUNDS);
  return hashed;
}

// contoh pakai
(async () => {
  const password = "admin123";
  const hash = await hashPassword(password);
  console.log("Hash:", hash);
})();