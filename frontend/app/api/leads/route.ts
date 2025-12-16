/**
 * API Route pro submit onboarding formuláře
 * Zachovává existující strukturu pro DB zápis
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Validace požadovaných polí
    if (!body.email) {
      return NextResponse.json(
        { error: 'Email is required' },
        { status: 400 }
      );
    }

    if (!body.description) {
      return NextResponse.json(
        { error: 'Description is required' },
        { status: 400 }
      );
    }

    // Validace struktury input_transform
    if (!body.input_transform) {
      return NextResponse.json(
        { error: 'input_transform is required' },
        { status: 400 }
      );
    }

    // API endpoint pro Supabase - použije se z env
    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY;

    if (!supabaseUrl || !supabaseServiceKey) {
      return NextResponse.json(
        { error: 'Server configuration error' },
        { status: 500 }
      );
    }

    // Volání Supabase API
    const response = await fetch(`${supabaseUrl}/rest/v1/junior_leads`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': supabaseServiceKey,
        'Authorization': `Bearer ${supabaseServiceKey}`,
        'Prefer': 'return=representation',
      },
      body: JSON.stringify({
        name: body.name || '',
        email: body.email,
        description: body.description,
        input_transform: body.input_transform,
        status: 'FLAGGED',
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      return NextResponse.json(
        { error: error || 'Failed to create lead' },
        { status: response.status }
      );
    }

    const result = await response.json();
    const leadId = Array.isArray(result) ? result[0]?.id : result.id;

    return NextResponse.json({ id: leadId, success: true });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
