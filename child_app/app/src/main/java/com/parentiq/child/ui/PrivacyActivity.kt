package com.parentiq.child.ui

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.parentiq.child.databinding.ActivityPrivacyBinding

class PrivacyActivity : AppCompatActivity() {

    private lateinit var binding: ActivityPrivacyBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPrivacyBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.btnUnderstood.setOnClickListener {
            finish()
        }
    }
}

