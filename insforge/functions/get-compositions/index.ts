const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

interface Composition {
  id?: string;
  name: string;
  patch_number: string;
  tier: string;
  winrate: number;
  top4rate: number;
  avg_placement: number;
  traits: string[];
  units: Record<string, unknown>[];
  items: Record<string, unknown>[];
  game_count: number;
}

const handler = async (req: Request): Promise<Response> => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  const url = new URL(req.url);
  const patch = url.searchParams.get("patch");
  const tier = url.searchParams.get("tier");
  const limit = parseInt(url.searchParams.get("limit") || "20");

  try {
    const compositions: Composition[] = [];
    return new Response(JSON.stringify({ data: compositions }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
};

export default handler;
