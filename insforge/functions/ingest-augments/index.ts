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

    const augments = [
      {
        name: "Jeweled Lotus",
        tier: "prismatic",
        description: "Start with +25 gold",
      },
      { name: "Aegis Crest", tier: "prismatic", description: "+200 armor" },
      { name: "Money Mgr", tier: "gold", description: "Interest +2" },
      { name: "Tinker", tier: "gold", description: "Shop reroll deals" },
      {
        name: "First Strike",
        tier: "silver",
        description: "First hit deals bonus",
      },
      { name: "Ensemble", tier: "silver", description: "+1 max trait" },
    ];

    return new Response(
      JSON.stringify({
        status: "completed",
        patch_number: patchNumber,
        count: augments.length,
        data: augments,
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
