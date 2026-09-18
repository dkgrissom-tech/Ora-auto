import { NextRequest, NextResponse } from "next/server";
import { createServiceClient } from "@/lib/supabase-server";

export async function GET(_req: NextRequest, { params }: { params: { id: string } }) {
  const service = createServiceClient();
  const { data: order } = await service
    .from("orders")
    .select("id, status, created_at, generations(preset_id, video_url)")
    .eq("id", params.id)
    .single();
  if (!order) return NextResponse.json({ error: "not found" }, { status: 404 });
  return NextResponse.json(order);
}
