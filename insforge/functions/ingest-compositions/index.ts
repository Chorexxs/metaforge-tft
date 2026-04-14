const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

interface Composition {
  name: string;
  patch_number: string;
  tier: string;
  winrate: number;
  top4rate: number;
  avg_placement: number;
  traits: string[];
  units: Record<string, unknown>[];
  items: Record<string, unknown>[];
}

const handler = async (req: Request): Promise<Response> => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const body = await req.json().catch(() => ({}));
    const patchNumber = body.patch_number || body.patch || "14.1";

    const compositions: Composition[] = [
      {
        name: "Example Comp - Hellfire Burn",
        patch_number: patchNumber,
        tier: "S",
        winrate: 52.5,
        top4rate: 78.0,
        avg_placement: 3.8,
        traits: ["Hellfire", "Trailblazer"],
        units: [
          { name: "Jinx", role: "carry", priority: "core" },
          { name: "Twitch", role: "flex", priority: "optional" },
        ],
        items: [],
      },
      {
        name: "Example Comp - Aegis Enforcers",
        patch_number: patchNumber,
        tier: "A",
        winrate: 48.0,
        top4rate: 72.0,
        avg_placement: 4.2,
        traits: ["Aegis", "Enforcer"],
        units: [
          { name: "Leona", role: "tank", priority: "core" },
          { name: "Nautilus", role: "tank", priority: "core" },
        ],
        items: [],
      },
    ];

    return new Response(
      JSON.stringify({
        status: "completed",
        patch_number: patchNumber,
        compositions_count: compositions.length,
        data: compositions,
      }),
      {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      },
    );
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
};

export default handler;
