import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import { env } from "./env";
import { readFile } from "node:fs/promises";

export const s3 = new S3Client({
  region: env.AWS_REGION,
  credentials: { accessKeyId: env.AWS_ACCESS_KEY_ID, secretAccessKey: env.AWS_SECRET_ACCESS_KEY },
});

export async function uploadFile(localPath: string, key: string, contentType = "video/mp4") {
  const Body = await readFile(localPath);
  await s3.send(new PutObjectCommand({ Bucket: env.S3_BUCKET, Key: key, Body, ContentType: contentType }));
  return `${env.S3_PUBLIC_BASE_URL}/${key}`;
}

export async function signedGet(key: string, expiresIn = 60 * 60 * 24 * 7) {
  return getSignedUrl(
    s3,
    new PutObjectCommand({ Bucket: env.S3_BUCKET, Key: key }),
    { expiresIn },
  );
}
