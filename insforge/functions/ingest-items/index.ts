const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

const handler = async (req: Request): Promise<Response> => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const body = await req.json().catch(() => ({}));
    const patchNumber = body.patch_number || "14.1";

    const items = [
      {
        key: "Deathblade",
        name: "Deathblade",
        description: "+30% crit damage",
      },
      {
        key: "GiantSlayer",
        name: "Giant Slayer",
        description: "+15% vs bigger",
      },
      { key: "InfinityEdge", name: "Infinity Edge", description: "100% crit" },
      { key: "Rabadons", name: "Rabadon's Deathcap", description: "+35% AP" },
      {
        key: "HoJ",
        name: "Hand of Justice",
        description: "+10 damage or +10 AP",
      },
      { key: "BT", name: "Bloodthirster", description: "Lifesteal + shield" },
    ];

    return new Response(
      JSON.stringify({
        status: "completed",
        patch_number: patchNumber,
        count: items.length,
        data: items,
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
