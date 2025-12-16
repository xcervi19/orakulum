/**
 * API client - zachovává existující API payload strukturu
 */

import { OnboardingFormData } from '@/types/onboarding';

/**
 * Submit handler - zachovává existující strukturu pro DB zápis
 * 
 * API payload struktura odpovídá schématu junior_leads:
 * - name: text
 * - email: text
 * - description: text (raw input)
 * - input_transform: jsonb (strukturovaná data)
 */
export async function submitOnboarding(data: OnboardingFormData): Promise<{ success: boolean; leadId?: string; error?: string }> {
  try {
    // Sestavení payloadu podle existující struktury
    const payload = {
      name: data.name || '',
      email: data.email,
      description: data.description, // Raw input zachován
      input_transform: {
        obor: data.inputTransform.obor,
        seniorita: data.inputTransform.seniorita,
        hlavni_cil: data.inputTransform.hlavni_cil,
        technologie: data.inputTransform.technologie,
        platove_ocekavani: data.inputTransform.platove_ocekavani,
        konkretnost: data.inputTransform.konkretnost,
        casovy_horizont: data.inputTransform.casovy_horizont,
        puvodni_text: data.description, // Zachování původního textu
      },
      status: 'FLAGGED', // Počáteční status pro pipeline
    };

    // API endpoint - použije se dynamicky z env nebo konfigurace
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/leads';
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.text();
      return { success: false, error: error || 'Failed to submit' };
    }

    const result = await response.json();
    return { success: true, leadId: result.id };
  } catch (error) {
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error' 
    };
  }
}
